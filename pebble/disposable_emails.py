"""Disposable / throwaway email domain blocklist (2026-05-24).

Marc 2026-05-24 security review: bot signup attacks need a fresh
email per account. Disposable-email services (mailinator, tempmail,
guerrillamail, etc.) make this near-free. Blocking the top ~60
domains raises the attack cost without bothering legit users.

The list is small + well-known on purpose: easy to maintain, no
remote fetch / cache dance, no false-positive against work emails.
We don't try to catch every throwaway provider — just the obvious
ones a casual bot would reach for first. Sophisticated attackers
can still use custom domains; that's where Turnstile + per-account
rate limits pick up the load.

The blocklist matches by the email's domain portion exactly OR by
suffix. "@mailinator.com" and "@whatever.mailinator.com" both
match — many throwaway services rotate subdomains daily.
"""
from __future__ import annotations


# Curated list of disposable / temporary email providers. Sorted
# alphabetically for diff-friendliness. To add a provider, drop the
# bare domain (no leading @, no www) anywhere alphabetical.
DISPOSABLE_DOMAINS: frozenset[str] = frozenset({
    "0wnd.net",
    "10minutemail.com",
    "10minutemail.net",
    "20mail.it",
    "anonbox.net",
    "burnermail.io",
    "burnthis.email",
    "deadaddress.com",
    "discard.email",
    "disposablemail.com",
    "dispostable.com",
    "dropmail.me",
    "emailondeck.com",
    "emailtemporanea.net",
    "emltmp.com",
    "fakeinbox.com",
    "fakemail.net",
    "fakemailgenerator.com",
    "getairmail.com",
    "getnada.com",
    "guerrillamail.com",
    "guerrillamail.de",
    "guerrillamail.net",
    "guerrillamail.org",
    "guerrillamailblock.com",
    "harakirimail.com",
    "haribu.com",
    "incognitomail.com",
    "incognitomail.net",
    "inboxalias.com",
    "jetable.org",
    "mail-temporaire.fr",
    "mailbox.in.ua",
    "mailcatch.com",
    "maildrop.cc",
    "mailexpire.com",
    "mailforspam.com",
    "mailinator.com",
    "mailinator.net",
    "mailinator.org",
    "mailmoat.com",
    "mailnesia.com",
    "mailnull.com",
    "mailsac.com",
    "mailtemp.info",
    "minutemail.com",
    "moakt.com",
    "mohmal.com",
    "mvrht.com",
    "mytemp.email",
    "nepwk.com",
    "nowmymail.com",
    "rcpt.at",
    "rootfest.net",
    "rppkn.com",
    "selfdestructingmail.com",
    "sharklasers.com",
    "spambog.com",
    "spambox.us",
    "tempail.com",
    "temp-mail.org",
    "temp-mail.ru",
    "tempmail.de",
    "tempmail.email",
    "tempmail.net",
    "tempmailaddress.com",
    "tempmail-uk.com",
    "throwam.com",
    "throwawaymail.com",
    "trashmail.com",
    "trashmail.de",
    "trbvn.com",
    "wegwerfemail.de",
    "yopmail.com",
    "yopmail.fr",
    "yopmail.net",
    "zetmail.com",
})


def is_disposable(email: str) -> bool:
    """Return True if the email's domain (or any parent suffix) is
    on the blocklist. Case-insensitive.

    Examples:
      is_disposable("alice@mailinator.com")        → True
      is_disposable("alice@sub.mailinator.com")    → True   (parent match)
      is_disposable("alice@gmail.com")             → False
      is_disposable("not even an email")           → False  (no @ — safe default)
    """
    if not isinstance(email, str):
        return False
    at = email.rfind("@")
    if at < 0 or at == len(email) - 1:
        return False
    domain = email[at + 1:].strip().lower()
    if not domain:
        return False
    if domain in DISPOSABLE_DOMAINS:
        return True
    # Suffix match — any parent domain on the list. Loop in case
    # mailinator.foo.bar.com tries to slip through (we'd match
    # foo.bar.com → bar.com → com and bail; only mailinator.com
    # itself would match the registered listing).
    parts = domain.split(".")
    for i in range(1, len(parts)):
        suffix = ".".join(parts[i:])
        if suffix in DISPOSABLE_DOMAINS:
            return True
    return False


__all__ = ["is_disposable", "DISPOSABLE_DOMAINS"]
