# QTM3 Phase 0 Deployment Checklist

## Pre-Deployment Verification

### Code Readiness
- [x] qtm3_core.py - Core functionality
- [x] qtm3 - CLI interface  
- [x] Migration scripts (v1 → v3)
- [x] Telemetry framework
- [x] Install script
- [x] Privacy notice

### Testing Status
- [ ] Manual testing on macOS
- [ ] Manual testing on Linux
- [ ] Migration from v1 verified
- [ ] Telemetry opt-in flow tested
- [ ] Performance baseline (<10s capture)

### Documentation
- [x] README with usage examples
- [x] Architecture documentation
- [x] Migration guide
- [ ] Quick start video (optional)

## Deployment Steps

### 1. Developer Laptops (Day 1)
```bash
# Clone repository
git clone [repo-url] ~/qtm3-deploy

# Run installer
cd ~/qtm3-deploy
chmod +x install_v3.sh
./install_v3.sh

# Verify installation
qtm3 --version
```

### 2. Telemetry Setup (Day 1)
```bash
# First run will prompt for consent
qtm3

# Verify telemetry
python3 ~/qtm3/telemetry.py
```

### 3. Data Migration (Day 2)
```bash
# For users with existing v1
python3 migrate_to_v3.py

# Verify migration
qtm3 view
```

### 4. Team Onboarding (Days 2-3)
- [ ] 30-min demo session
- [ ] Share quick reference card
- [ ] Set up Slack channel for feedback
- [ ] Daily standup check-ins

### 5. Metrics Collection (Days 3-7)
- [ ] Monitor telemetry dashboard
- [ ] Track KPIs:
  - Capture latency
  - Daily active users
  - Task completion rate
  - Error frequency

## Success Criteria

### Week 1 Exit
- [ ] 5+ developers using daily
- [ ] Avg capture time <10s
- [ ] Zero critical bugs
- [ ] Positive feedback score (>7/10)
- [ ] Baseline metrics established

## Rollback Plan

If critical issues:
```bash
# Disable qtm3
rm ~/.local/bin/qtm3

# Restore v1
cd ~/qwen_task_manager
./run_task_manager.zsh
```

## Support Resources

- **Slack**: #qtm3-support
- **Wiki**: [Internal wiki link]
- **Issues**: GitHub issues with 'phase-0' label
- **Lead**: [Dev Lead contact]

## Next Actions

1. [ ] Schedule deployment kickoff (30 min)
2. [ ] Create feedback form
3. [ ] Set up metrics dashboard
4. [ ] Book Week 1 planning session

---

*Once all boxes checked, proceed with deployment*