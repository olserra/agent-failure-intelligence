# Security policy

## Scope

This project is a *testing harness* for agent failures. The simulated
environment contains no real secrets, services, or data by design.

## Reporting a vulnerability

If you find a security issue in this repository — for example a way the
harness itself could touch the real filesystem or network, or leaked
credentials in history — please report it privately via GitHub's private
vulnerability reporting ("Security" tab → "Report a vulnerability").

Please do not open public issues for unpatched vulnerabilities.

We ask reporters to:

- give us a reasonable window to reproduce and fix before public disclosure;
- avoid accessing, modifying, or exfiltrating anyone's data;
- avoid degrading any service.

We commit to acknowledging reports and communicating honestly about
timelines. This is a personal open-source project without a bug bounty
budget; we can offer credit in the advisory and our thanks.

## Publishing security results

Results about *this* harness are published only after they have been
executed and verified. Illustrative examples are always labeled as such.
