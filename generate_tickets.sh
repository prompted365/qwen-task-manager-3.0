#!/usr/bin/env bash

# QTM3 Sprint Ticket Generator
# Creates JIRA-style tickets for Week 1-5 implementation

set -e

TICKETS_DIR="$(dirname "$0")/tickets"
mkdir -p "$TICKETS_DIR"

# Week 1 Tickets
cat > "$TICKETS_DIR/WEEK1-001-file-watcher.md" << 'EOF'
# WEEK1-001: Implement File Watcher Daemon

## Objective
Create perception agent for monitoring project directories

## Acceptance Criteria
- [ ] Python watchdog integration
- [ ] Respects .gitignore patterns
- [ ] 1MB file size cap
- [ ] 5-second debounce
- [ ] Outputs only hash + path (perception locked)

## Technical Notes
- Use `watchdog` library
- Store config in `~/.qtm3/watcher.conf`
- Log to `~/.qtm3/logs/watcher.log`

## QA Gate
No PII leakage beyond hash + path

## Estimate: 2 days
EOF

cat > "$TICKETS_DIR/WEEK1-002-calendar-poller.md" << 'EOF'
# WEEK1-002: Calendar ICS Poller

## Objective
Monitor and parse .ics files for task integration

## Acceptance Criteria
- [ ] Poll ~/.calendar/*.ics every 30 min
- [ ] Parse VEVENT blocks
- [ ] Extract summary, due dates
- [ ] Write back new events
- [ ] Handle timezones correctly

## Technical Notes
- Use `icalendar` library
- Consider recurring events
- Cache parsed state

## QA Gate
Bidirectional sync without duplicates

## Estimate: 3 days
EOF

# Week 2 Tickets
cat > "$TICKETS_DIR/WEEK2-001-agent-split.md" << 'EOF'
# WEEK2-001: Split Monolith into Agent Services

## Objective
Refactor qtm3_core.py into modular agents

## Acceptance Criteria
- [ ] Extract Perception agent
- [ ] Extract Memory agent  
- [ ] Extract Reasoning agent
- [ ] Extract Exchange agent
- [ ] Unix socket IPC
- [ ] <300ms latency budget

## Technical Notes
- See agents.py prototype
- Maintain backwards compatibility
- Add health checks

## QA Gate
All agents respond to ping in <10ms

## Estimate: 3 days
EOF

# Week 3 Tickets
cat > "$TICKETS_DIR/WEEK3-001-vector-service.md" << 'EOF'
# WEEK3-001: Vector Embedding Service

## Objective
Build high-performance vector indexing

## Acceptance Criteria
- [ ] Python prototype with sentence-transformers
- [ ] Profile performance bottlenecks
- [ ] Port hot paths to Rust
- [ ] REST API interface
- [ ] Batch processing support

## Technical Notes
- Start with all-MiniLM-L6-v2 model
- Use tantivy for Rust backend
- Target: 1000 docs/sec

## QA Gate
Context accuracy ≥85% on test set

## Estimate: 5 days
EOF

# Week 4 Tickets
cat > "$TICKETS_DIR/WEEK4-001-energy-vectors.md" << 'EOF'
# WEEK4-001: Behavioral Energy Vector Space

## Objective
Implement energy/emotion tracking in task embeddings

## Acceptance Criteria
- [ ] Extend task schema with energy vectors
- [ ] Energy-aware prioritization
- [ ] Reflection trigger system
- [ ] Desktop notifications via `at`
- [ ] Energy correlation analysis

## Technical Notes
- 5D vector: physical, mental, emotional, social, spiritual
- Use cosine similarity for matching
- Trigger reflections at energy troughs

## QA Gate
Reflection adherence ≥90% of task days

## Estimate: 4 days
EOF

# Week 5 Tickets
cat > "$TICKETS_DIR/WEEK5-001-multi-user.md" << 'EOF'
# WEEK5-001: Multi-User Configuration

## Objective
Support multiple user profiles and workspaces

## Acceptance Criteria
- [ ] Config-driven workspace root
- [ ] User profile switching
- [ ] Isolated databases per profile
- [ ] Shared prompt templates
- [ ] Migration between profiles

## Technical Notes
- Store profiles in ~/.qtm3/profiles/
- Use QTM3_PROFILE env var
- Consider XDG base dirs

## QA Gate
Clean install works on macOS + Linux

## Estimate: 2 days
EOF

# Generate Sprint Board
cat > "$TICKETS_DIR/SPRINT_BOARD.md" << 'EOF'
# QTM3 Sprint Board

## Phase 0 (Current) ✅
- [x] Core implementation deployed
- [x] Migration tooling ready
- [x] Telemetry framework
- [ ] Deploy to 5+ developers

## Week 1 Sprint
- [ ] WEEK1-001: File Watcher Daemon
- [ ] WEEK1-002: Calendar Poller
- [ ] QA Gate: Perception locking verified

## Week 2 Sprint  
- [ ] WEEK2-001: Agent Service Split
- [ ] WEEK2-002: IPC Performance Tuning
- [ ] QA Gate: <300ms agent latency

## Week 3 Sprint
- [ ] WEEK3-001: Vector Embedding Service
- [ ] WEEK3-002: Rust Performance Port
- [ ] QA Gate: 85% context accuracy

## Week 4 Sprint
- [ ] WEEK4-001: Energy Vector Space
- [ ] WEEK4-002: Reflection Triggers
- [ ] QA Gate: 90% reflection adherence

## Week 5 Sprint
- [ ] WEEK5-001: Multi-User Support
- [ ] WEEK5-002: Documentation
- [ ] QA Gate: Fresh install success

## Metrics Dashboard
- Capture Latency: ⏱️ Tracking...
- Throughput Lift: 📈 Baseline set
- Context Accuracy: 🎯 Pending Week 3
- Energy Alignment: 🔋 Pending Week 4
EOF

echo "✅ Sprint tickets generated in $TICKETS_DIR"
echo ""
echo "Next steps:"
echo "1. Review tickets with team"
echo "2. Assign owners"
echo "3. Import to project board"
echo "4. Start Week 1 sprint"