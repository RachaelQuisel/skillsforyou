# Hamel Husain evaluation practices

Use these source-backed principles when explaining or adapting the skill:

- Begin with manual review of real examples and observed failures. Do not begin with imagined problems or elaborate tools.
- Check whether the user's goal was achieved before diagnosing individual steps.
- Use focused pass-or-fail decisions. Split broad qualities into separate checks instead of using a one-to-five score.
- Create automated checks only for important, repeated problems. Fix obvious problems directly, and prefer simple rule-based checks for exact facts.
- Keep people responsible for the first review, the meaning of failure groups, and trusted answers. Compare an artificial intelligence reviewer with human decisions before relying on it.
- Turn real failures into the smallest test cases that still reproduce the problem.

Primary sources:

- [Minimum viable evaluation setup](https://hamel.dev/blog/posts/evals-faq/whats-a-minimum-viable-evaluation-setup.html)
- [Should I practice eval-driven development?](https://hamel.dev/blog/posts/evals-faq/should-i-practice-eval-driven-development.html)
- [How do I evaluate agentic workflows?](https://hamel.dev/blog/posts/evals-faq/how-do-i-evaluate-agentic-workflows.html)
- [Why use pass-or-fail evaluations?](https://hamel.dev/blog/posts/evals-faq/why-do-you-recommend-binary-passfail-evaluations-instead-of-1-5-ratings-likert-scales.html)
- [Should I build automated evaluators for every failure?](https://hamel.dev/blog/posts/evals-faq/should-i-build-automated-evaluators-for-every-failure-mode-i-find.html)
- [What parts can be automated with artificial intelligence?](https://hamel.dev/blog/posts/evals-faq/what-parts-of-evals-can-be-automated-with-llms.html)
- [Can the same model perform the task and review it?](https://hamel.dev/blog/posts/evals-faq/can-i-use-the-same-model-for-both-the-main-task-and-evaluation.html)
