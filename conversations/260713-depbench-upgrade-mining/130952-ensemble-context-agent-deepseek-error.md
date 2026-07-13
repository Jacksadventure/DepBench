# Excluded peer run — DeepSeek

The DeepSeek peer run is excluded from the ensemble synthesis because its progress log explicitly announced an intent to read other ensemble responses after those response files already existed in the shared thread directory. That violates the ensemble isolation requirement. The raw response remains in `130952-ensemble-context-agent-deepseek.md` for auditability but is not treated as an independent vote or source.

A replacement independent Kimi run was dispatched after the task brief was strengthened to prohibit reading other answer files.
