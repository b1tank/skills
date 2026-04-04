#!/usr/bin/env python3
"""
Sends Claude Code traces to Langfuse after each response.
Supports both main conversation and subagent (Task) traces with nested waterfall rendering.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Check if Langfuse is available
try:
    from langfuse import Langfuse
except ImportError:
    print("Error: langfuse package not installed. Run: pip install langfuse", file=sys.stderr)
    sys.exit(0)

# Configuration
LOG_FILE = Path.home() / ".claude" / "state" / "langfuse_hook.log"
STATE_FILE = Path.home() / ".claude" / "state" / "langfuse_state.json"
DEBUG = os.environ.get("CC_LANGFUSE_DEBUG", "").lower() == "true"


def log(level: str, message: str) -> None:
    """Log a message to the log file."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"{timestamp} [{level}] {message}\n")


def debug(message: str) -> None:
    """Log a debug message (only if DEBUG is enabled)."""
    if DEBUG:
        log("DEBUG", message)


def load_state() -> dict:
    """Load the state file containing session tracking info."""
    if not STATE_FILE.exists():
        return {}
    try:
        return json.loads(STATE_FILE.read_text())
    except (json.JSONDecodeError, IOError):
        return {}


def save_state(state: dict) -> None:
    """Save the state file."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


def get_content(msg: dict) -> Any:
    """Extract content from a message."""
    if isinstance(msg, dict):
        if "message" in msg:
            return msg["message"].get("content")
        return msg.get("content")
    return None


def is_tool_result(msg: dict) -> bool:
    """Check if a message contains tool results."""
    content = get_content(msg)
    if isinstance(content, list):
        return any(
            isinstance(item, dict) and item.get("type") == "tool_result"
            for item in content
        )
    return False


def get_tool_calls(msg: dict) -> list:
    """Extract tool use blocks from a message."""
    content = get_content(msg)
    if isinstance(content, list):
        return [
            item for item in content
            if isinstance(item, dict) and item.get("type") == "tool_use"
        ]
    return []


def get_text_content(msg: dict) -> str:
    """Extract text content from a message."""
    content = get_content(msg)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                text_parts.append(item.get("text", ""))
            elif isinstance(item, str):
                text_parts.append(item)
        return "\n".join(text_parts)
    return ""


def merge_assistant_parts(parts: list) -> dict:
    """Merge multiple assistant message parts into one."""
    if not parts:
        return {}

    merged_content = []
    for part in parts:
        content = get_content(part)
        if isinstance(content, list):
            merged_content.extend(content)
        elif content:
            merged_content.append({"type": "text", "text": str(content)})

    # Use the structure from the first part
    result = parts[0].copy()
    if "message" in result:
        result["message"] = result["message"].copy()
        result["message"]["content"] = merged_content
    else:
        result["content"] = merged_content

    return result


# ---------------------------------------------------------------------------
# Subagent discovery & parsing
# ---------------------------------------------------------------------------

def find_subagent_files(transcript_file: Path, session_id: str) -> dict[str, Path]:
    """Discover subagent JSONL files for a given session.

    Claude Code stores subagent transcripts at:
        <project_dir>/<sessionId>/subagents/agent-<agentId>.jsonl

    Returns a dict mapping agentId -> file path.
    """
    subagents_dir = transcript_file.parent / session_id / "subagents"
    if not subagents_dir.exists():
        return {}

    result: dict[str, Path] = {}
    for f in subagents_dir.glob("agent-*.jsonl"):
        agent_id = f.stem.removeprefix("agent-")
        result[agent_id] = f

    if result:
        debug(f"Found {len(result)} subagent file(s): {list(result.keys())}")
    return result


def get_agent_id_from_tool_result(tool_id: str, tool_results: list) -> str | None:
    """Extract the agentId from a Task tool_result message.

    When a Task (subagent) tool completes, the tool_result message in the main
    JSONL contains toolUseResult.agentId linking to the subagent file.
    """
    for tr in tool_results:
        tr_content = get_content(tr)
        if isinstance(tr_content, list):
            for item in tr_content:
                if isinstance(item, dict) and item.get("tool_use_id") == tool_id:
                    # Found the matching tool_result — check the parent msg
                    # for toolUseResult.agentId
                    tool_use_result = tr.get("toolUseResult", {})
                    if isinstance(tool_use_result, dict):
                        return tool_use_result.get("agentId")
    return None


def parse_subagent_turns(subagent_file: Path) -> list[dict]:
    """Parse a subagent JSONL file into a list of turn dicts.

    Each turn dict has:
        user_msg:       the user message that started the turn
        assistant_msgs: list of merged assistant messages
        tool_results:   list of tool_result messages
        model:          model name from first assistant message

    Uses the same grouping logic as process_transcript but operates on
    a full file and returns structured data instead of creating traces.
    """
    try:
        lines = subagent_file.read_text().strip().split("\n")
    except IOError as e:
        debug(f"Error reading subagent file {subagent_file}: {e}")
        return []

    messages = []
    for line in lines:
        try:
            msg = json.loads(line)
            messages.append(msg)
        except json.JSONDecodeError:
            continue

    turns: list[dict] = []
    current_user = None
    current_assistants: list[dict] = []
    current_assistant_parts: list[dict] = []
    current_msg_id: str | None = None
    current_tool_results: list[dict] = []

    def _finalize_turn():
        nonlocal current_user, current_assistants, current_assistant_parts
        nonlocal current_msg_id, current_tool_results

        # Flush any pending assistant parts
        if current_msg_id and current_assistant_parts:
            merged = merge_assistant_parts(current_assistant_parts)
            current_assistants.append(merged)

        if current_user and current_assistants:
            model = "claude"
            first_a = current_assistants[0]
            if isinstance(first_a, dict) and "message" in first_a:
                model = first_a["message"].get("model", "claude")

            turns.append({
                "user_msg": current_user,
                "assistant_msgs": current_assistants,
                "tool_results": current_tool_results,
                "model": model,
            })

    for msg in messages:
        role = msg.get("type") or (msg.get("message", {}).get("role"))

        if role == "user":
            if is_tool_result(msg):
                current_tool_results.append(msg)
                continue

            # New user message — finalize previous turn
            _finalize_turn()

            current_user = msg
            current_assistants = []
            current_assistant_parts = []
            current_msg_id = None
            current_tool_results = []

        elif role == "assistant":
            msg_id = None
            if isinstance(msg, dict) and "message" in msg:
                msg_id = msg["message"].get("id")

            if not msg_id:
                current_assistant_parts.append(msg)
            elif msg_id == current_msg_id:
                current_assistant_parts.append(msg)
            else:
                if current_msg_id and current_assistant_parts:
                    merged = merge_assistant_parts(current_assistant_parts)
                    current_assistants.append(merged)
                current_msg_id = msg_id
                current_assistant_parts = [msg]

    # Final turn
    _finalize_turn()

    debug(f"Parsed {len(turns)} turn(s) from subagent file {subagent_file.name}")
    return turns


def create_subagent_spans(
    langfuse: Langfuse,
    agent_id: str,
    description: str,
    subagent_file: Path,
    subagent_usage: dict | None,
) -> None:
    """Create nested Langfuse spans for a subagent's work.

    Called inside an already-open parent span (the Task tool span).
    Creates:
        Subagent: <agentId> - <description>  (span, wrapping all turns)
          ├── Subagent Turn 1  (span)
          │   ├── Claude Response  (generation)
          │   ├── Tool: Read       (span)
          │   └── Tool: Edit       (span)
          └── Subagent Turn 2  (span)
              └── ...
    """
    turns = parse_subagent_turns(subagent_file)
    if not turns:
        debug(f"No turns parsed for subagent {agent_id}")
        return

    metadata: dict[str, Any] = {
        "agent_id": agent_id,
        "source": "claude-code-subagent",
    }
    if subagent_usage:
        metadata["total_tokens"] = subagent_usage.get("totalTokens")
        metadata["total_tool_uses"] = subagent_usage.get("totalToolUseCount")
        metadata["duration_ms"] = subagent_usage.get("totalDurationMs")

    label = f"Subagent: {agent_id}"
    if description:
        label = f"Subagent: {agent_id} — {description}"

    with langfuse.start_as_current_span(
        name=label,
        metadata=metadata,
    ) as subagent_span:
        for turn_idx, turn in enumerate(turns, start=1):
            user_text = get_text_content(turn["user_msg"])
            final_output = ""
            if turn["assistant_msgs"]:
                final_output = get_text_content(turn["assistant_msgs"][-1])

            # Collect tool calls for this turn
            turn_tool_calls: list[dict] = []
            for assistant_msg in turn["assistant_msgs"]:
                for tc in get_tool_calls(assistant_msg):
                    tool_name = tc.get("name", "unknown")
                    tool_input = tc.get("input", {})
                    tool_id = tc.get("id", "")

                    tool_output = None
                    for tr in turn["tool_results"]:
                        tr_content = get_content(tr)
                        if isinstance(tr_content, list):
                            for item in tr_content:
                                if isinstance(item, dict) and item.get("tool_use_id") == tool_id:
                                    tool_output = item.get("content")
                                    break

                    turn_tool_calls.append({
                        "name": tool_name,
                        "input": tool_input,
                        "output": tool_output,
                        "id": tool_id,
                    })

            with langfuse.start_as_current_span(
                name=f"Subagent Turn {turn_idx}",
                input={"role": "user", "content": user_text[:500]},
                metadata={"turn_index": turn_idx},
            ) as turn_span:
                # Generation
                with langfuse.start_as_current_observation(
                    name="Claude Response",
                    as_type="generation",
                    model=turn["model"],
                    input={"role": "user", "content": user_text[:500]},
                    output={"role": "assistant", "content": final_output[:2000]},
                    metadata={"tool_count": len(turn_tool_calls)},
                ):
                    pass

                # Tool spans
                for tc in turn_tool_calls:
                    with langfuse.start_as_current_span(
                        name=f"Tool: {tc['name']}",
                        input=tc["input"],
                        metadata={
                            "tool_name": tc["name"],
                            "tool_id": tc["id"],
                        },
                    ) as ts:
                        ts.update(output=tc["output"])

                turn_span.update(output={"role": "assistant", "content": final_output[:2000]})

        # Update outer subagent span with summary
        last_turn = turns[-1]
        last_output = get_text_content(last_turn["assistant_msgs"][-1]) if last_turn["assistant_msgs"] else ""
        subagent_span.update(output={"summary": last_output[:2000], "turns": len(turns)})

    debug(f"Created subagent spans for {agent_id} ({len(turns)} turns)")


# ---------------------------------------------------------------------------
# Main transcript discovery
# ---------------------------------------------------------------------------

def find_latest_transcript() -> tuple[str, Path] | None:
    """Find the most recently modified transcript file.

    Claude Code stores transcripts as *.jsonl files directly in the project directory.
    Main conversation files have UUID names, agent files have agent-*.jsonl names.
    The session ID is stored inside each JSON line.
    """
    projects_dir = Path.home() / ".claude" / "projects"

    if not projects_dir.exists():
        debug(f"Projects directory not found: {projects_dir}")
        return None

    latest_file = None
    latest_mtime = 0

    for project_dir in projects_dir.iterdir():
        if not project_dir.is_dir():
            continue

        # Look for all .jsonl files directly in the project directory
        for transcript_file in project_dir.glob("*.jsonl"):
            mtime = transcript_file.stat().st_mtime
            if mtime > latest_mtime:
                latest_mtime = mtime
                latest_file = transcript_file

    if latest_file:
        # Extract session ID from the first line of the file
        try:
            first_line = latest_file.read_text().split("\n")[0]
            first_msg = json.loads(first_line)
            session_id = first_msg.get("sessionId", latest_file.stem)
            debug(f"Found transcript: {latest_file}, session: {session_id}")
            return (session_id, latest_file)
        except (json.JSONDecodeError, IOError, IndexError) as e:
            debug(f"Error reading transcript {latest_file}: {e}")
            return None

    debug("No transcript files found")
    return None


# ---------------------------------------------------------------------------
# Trace creation
# ---------------------------------------------------------------------------

def create_trace(
    langfuse: Langfuse,
    session_id: str,
    turn_num: int,
    user_msg: dict,
    assistant_msgs: list,
    tool_results: list,
    subagent_files: dict[str, Path] | None = None,
) -> None:
    """Create a Langfuse trace for a single turn.

    When a tool call is a Task (subagent), and the corresponding subagent JSONL
    file exists, nested spans are created for the subagent's internal turns
    instead of a flat tool span.
    """
    if subagent_files is None:
        subagent_files = {}

    # Extract user text
    user_text = get_text_content(user_msg)

    # Extract final assistant text
    final_output = ""
    if assistant_msgs:
        final_output = get_text_content(assistant_msgs[-1])

    # Get model info from first assistant message
    model = "claude"
    if assistant_msgs and isinstance(assistant_msgs[0], dict) and "message" in assistant_msgs[0]:
        model = assistant_msgs[0]["message"].get("model", "claude")

    # Collect all tool calls and results
    all_tool_calls: list[dict] = []
    for assistant_msg in assistant_msgs:
        tool_calls = get_tool_calls(assistant_msg)
        for tool_call in tool_calls:
            tool_name = tool_call.get("name", "unknown")
            tool_input = tool_call.get("input", {})
            tool_id = tool_call.get("id", "")

            # Find matching tool result
            tool_output = None
            agent_id: str | None = None
            subagent_usage: dict | None = None
            for tr in tool_results:
                tr_content = get_content(tr)
                if isinstance(tr_content, list):
                    for item in tr_content:
                        if isinstance(item, dict) and item.get("tool_use_id") == tool_id:
                            tool_output = item.get("content")
                            break

                # Check for agentId in toolUseResult (for Task tool calls)
                tur = tr.get("toolUseResult", {})
                if isinstance(tur, dict) and tur.get("agentId"):
                    # Only match if this tool_result corresponds to our tool_id
                    tr_content_check = get_content(tr)
                    if isinstance(tr_content_check, list):
                        for item in tr_content_check:
                            if isinstance(item, dict) and item.get("tool_use_id") == tool_id:
                                agent_id = tur.get("agentId")
                                subagent_usage = tur
                                break

            all_tool_calls.append({
                "name": tool_name,
                "input": tool_input,
                "output": tool_output,
                "id": tool_id,
                "agent_id": agent_id,
                "subagent_usage": subagent_usage,
            })

    # Create trace using the new API with context managers
    with langfuse.start_as_current_span(
        name=f"Turn {turn_num}",
        input={"role": "user", "content": user_text},
        metadata={
            "source": "claude-code",
            "turn_number": turn_num,
            "session_id": session_id,
        },
    ) as trace_span:
        # Create generation for the LLM response
        with langfuse.start_as_current_observation(
            name="Claude Response",
            as_type="generation",
            model=model,
            input={"role": "user", "content": user_text},
            output={"role": "assistant", "content": final_output},
            metadata={
                "tool_count": len(all_tool_calls),
            },
        ):
            pass  # Generation is auto-completed when exiting context

        # Create spans for tool calls
        for tool_call in all_tool_calls:
            tc_name = tool_call["name"]
            tc_agent_id = tool_call.get("agent_id")

            # If this is a Task (subagent) call with a matching subagent file,
            # render the subagent's internal turns as nested spans.
            if tc_name == "Task" and tc_agent_id and tc_agent_id in subagent_files:
                description = ""
                if isinstance(tool_call["input"], dict):
                    description = tool_call["input"].get("description", "")

                with langfuse.start_as_current_span(
                    name=f"Tool: Task ({tc_agent_id})",
                    input=tool_call["input"],
                    metadata={
                        "tool_name": tc_name,
                        "tool_id": tool_call["id"],
                        "agent_id": tc_agent_id,
                    },
                ) as task_span:
                    create_subagent_spans(
                        langfuse,
                        agent_id=tc_agent_id,
                        description=description,
                        subagent_file=subagent_files[tc_agent_id],
                        subagent_usage=tool_call.get("subagent_usage"),
                    )
                    # Truncate large subagent output for the outer span
                    output_text = tool_call["output"]
                    if isinstance(output_text, str) and len(output_text) > 2000:
                        output_text = output_text[:2000] + "..."
                    elif isinstance(output_text, list):
                        # tool_output can be a list of content blocks
                        output_text = str(output_text)[:2000]
                    task_span.update(output=output_text)

                debug(f"Created nested subagent span for Task agent {tc_agent_id}")
            else:
                # Regular tool call — flat span
                with langfuse.start_as_current_span(
                    name=f"Tool: {tc_name}",
                    input=tool_call["input"],
                    metadata={
                        "tool_name": tc_name,
                        "tool_id": tool_call["id"],
                    },
                ) as tool_span:
                    tool_span.update(output=tool_call["output"])
                debug(f"Created span for tool: {tc_name}")

        # Update trace with output
        trace_span.update(output={"role": "assistant", "content": final_output})

    debug(f"Created trace for turn {turn_num}")


# ---------------------------------------------------------------------------
# Transcript processing
# ---------------------------------------------------------------------------

def process_transcript(langfuse: Langfuse, session_id: str, transcript_file: Path, state: dict) -> int:
    """Process a transcript file and create traces for new turns."""
    # Get previous state for this session
    session_state = state.get(session_id, {})
    last_line = session_state.get("last_line", 0)
    turn_count = session_state.get("turn_count", 0)

    # Read transcript
    lines = transcript_file.read_text().strip().split("\n")
    total_lines = len(lines)

    if last_line >= total_lines:
        debug(f"No new lines to process (last: {last_line}, total: {total_lines})")
        return 0

    # Parse new messages
    new_messages = []
    for i in range(last_line, total_lines):
        try:
            msg = json.loads(lines[i])
            new_messages.append(msg)
        except json.JSONDecodeError:
            continue

    if not new_messages:
        return 0

    debug(f"Processing {len(new_messages)} new messages")

    # Discover subagent files for this session
    subagent_files = find_subagent_files(transcript_file, session_id)

    # Group messages into turns (user -> assistant(s) -> tool_results)
    turns = 0
    current_user = None
    current_assistants: list[dict] = []
    current_assistant_parts: list[dict] = []
    current_msg_id: str | None = None
    current_tool_results: list[dict] = []

    for msg in new_messages:
        role = msg.get("type") or (msg.get("message", {}).get("role"))

        if role == "user":
            # Check if this is a tool result
            if is_tool_result(msg):
                current_tool_results.append(msg)
                continue

            # New user message - finalize previous turn
            if current_msg_id and current_assistant_parts:
                merged = merge_assistant_parts(current_assistant_parts)
                current_assistants.append(merged)
                current_assistant_parts = []
                current_msg_id = None

            if current_user and current_assistants:
                turns += 1
                turn_num = turn_count + turns
                create_trace(langfuse, session_id, turn_num, current_user, current_assistants, current_tool_results, subagent_files)

            # Start new turn
            current_user = msg
            current_assistants = []
            current_assistant_parts = []
            current_msg_id = None
            current_tool_results = []

        elif role == "assistant":
            msg_id = None
            if isinstance(msg, dict) and "message" in msg:
                msg_id = msg["message"].get("id")

            if not msg_id:
                # No message ID, treat as continuation
                current_assistant_parts.append(msg)
            elif msg_id == current_msg_id:
                # Same message ID, add to current parts
                current_assistant_parts.append(msg)
            else:
                # New message ID - finalize previous message
                if current_msg_id and current_assistant_parts:
                    merged = merge_assistant_parts(current_assistant_parts)
                    current_assistants.append(merged)

                # Start new assistant message
                current_msg_id = msg_id
                current_assistant_parts = [msg]

    # Process final turn
    if current_msg_id and current_assistant_parts:
        merged = merge_assistant_parts(current_assistant_parts)
        current_assistants.append(merged)

    if current_user and current_assistants:
        turns += 1
        turn_num = turn_count + turns
        create_trace(langfuse, session_id, turn_num, current_user, current_assistants, current_tool_results, subagent_files)

    # Update state
    state[session_id] = {
        "last_line": total_lines,
        "turn_count": turn_count + turns,
        "updated": datetime.now(timezone.utc).isoformat(),
    }
    save_state(state)

    return turns


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    script_start = datetime.now()
    debug("Hook started")

    # Check if tracing is enabled
    if os.environ.get("TRACE_TO_LANGFUSE", "").lower() != "true":
        debug("Tracing disabled (TRACE_TO_LANGFUSE != true)")
        sys.exit(0)

    # Check for required environment variables
    public_key = os.environ.get("CC_LANGFUSE_PUBLIC_KEY") or os.environ.get("LANGFUSE_PUBLIC_KEY")
    secret_key = os.environ.get("CC_LANGFUSE_SECRET_KEY") or os.environ.get("LANGFUSE_SECRET_KEY")
    host = os.environ.get("CC_LANGFUSE_HOST") or os.environ.get("LANGFUSE_HOST", "https://cloud.langfuse.com")

    if not public_key or not secret_key:
        log("ERROR", "Langfuse API keys not set (CC_LANGFUSE_PUBLIC_KEY / CC_LANGFUSE_SECRET_KEY)")
        sys.exit(0)

    # Initialize Langfuse client
    try:
        langfuse = Langfuse(
            public_key=public_key,
            secret_key=secret_key,
            host=host,
        )
    except Exception as e:
        log("ERROR", f"Failed to initialize Langfuse client: {e}")
        sys.exit(0)

    # Load state
    state = load_state()

    # Find the most recently modified transcript
    result = find_latest_transcript()
    if not result:
        debug("No transcript file found")
        sys.exit(0)

    session_id, transcript_file = result

    if not transcript_file:
        debug("No transcript file found")
        sys.exit(0)

    debug(f"Processing session: {session_id}")

    # Process the transcript
    try:
        turns = process_transcript(langfuse, session_id, transcript_file, state)

        # Flush to ensure all data is sent
        langfuse.flush()

        # Log execution time
        duration = (datetime.now() - script_start).total_seconds()
        log("INFO", f"Processed {turns} turns in {duration:.1f}s")

        if duration > 180:
            log("WARN", f"Hook took {duration:.1f}s (>3min), consider optimizing")

    except Exception as e:
        log("ERROR", f"Failed to process transcript: {e}")
        import traceback
        debug(traceback.format_exc())
    finally:
        langfuse.shutdown()

    sys.exit(0)


if __name__ == "__main__":
    main()