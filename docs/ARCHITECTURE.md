# System Architecture

```text
User
  ↓
Secure Web Interface
  ↓
Password Input
  ↓
In-Memory Analysis
  ├── Length Analyzer
  ├── Character Analyzer
  ├── Common Password Checker
  ├── Sequence Detector
  ├── Keyboard Pattern Detector
  ├── Repetition Detector
  ├── Context Checker
  └── Entropy Estimator
  ↓
Strength Scoring Engine
  ↓
Classification
  ↓
Suggestion Engine
  ↓
User

Optional safe aggregate metrics
  ↓
SQLite Analytics
  ↓
Dashboard
```

The uploaded project specification explicitly requires that the password itself must not enter analytics storage.
