import json
from pathlib import Path
import sys
sys.path.insert(0, '.')
from gryphon_ai.trace_analyzer import TraceAnalyzer

# Load a trace file
trace_dir = Path.home() / '.gryphon_ai' / 'traces' / 'derBestCaseScenarioV5' / '20260202_105413'
tg_file = trace_dir / 'trace.tg'

with open(tg_file, 'r', encoding='utf-8') as f:
    tg_data = json.load(f)

# Get the first trace
first_trace = tg_data['traces'][0]

print("=" * 80)
print("RAW TRACE DATA (first trace):")
print("=" * 80)
print(f"Trace structure: {type(first_trace)}")
print(f"Length: {len(first_trace)} elements")
print(f"\nElement 0 (mark): {first_trace[0]}")
print(f"Element 1 (probability): {first_trace[1]}")
print(f"Element 2 (nodes/events): {len(first_trace[2])} events")
print(f"Element 3 (IN edges): {len(first_trace[3])} edges")
print(f"Element 4 (FOLLOWS edges): {len(first_trace[4])} edges")
print(f"\nFirst 3 events (raw):")
for i, node in enumerate(first_trace[2][:3]):
    print(f"  {i}: {node}")

print("\n" + "=" * 80)
print("EXTRACTED TRACE SUMMARY:")
print("=" * 80)

# Extract summary for first trace
extracted = TraceAnalyzer.extract_trace_summary(first_trace, 0)

print(json.dumps(extracted, indent=2))

print("\n" + "=" * 80)
print("EXPLANATION:")
print("=" * 80)
print(f"i: {extracted['i']} - trace index")
print(f"m: {extracted['m']} - mark (U=unique, M=multiple)")
print(f"p: {extracted['p']} - probability")
print(f"seq: {len(extracted['seq'])} events - event sequence in order")
print(f"in: {len(extracted['in'])} relations - IN relation edges")
print(f"fol: {len(extracted['fol'])} relations - FOLLOWS relation edges")
print(f"\nEvent sequence (first 10): {' -> '.join(extracted['seq'][:10])}")
if extracted['in']:
    print(f"\nIN relations (first 5): {', '.join(extracted['in'][:5])}")
if extracted['fol']:
    print(f"\nFOLLOWS relations (first 5): {', '.join(extracted['fol'][:5])}")
