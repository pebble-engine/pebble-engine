/**
 * Disposable / throwaway email domain blocklist (v3 mirror).
 *
 * Sibling of pebble/disposable_emails.py — same list, same matching
 * semantics. Duplicated here so the v3 precheck route handler can
 * decide in <1ms without an engine round-trip. If either copy drifts,
 * the integration test in tests/test_disposable_emails.py + the v3
 * unit test below will diverge.
 *
 * To add a provider: update BOTH files. Bare domain (no leading @,
 * no www). Alphabetical for diff-friendliness.
 */

const DISPOSABLE_DOMAINS: ReadonlySet<string> = new Set([
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
]);

export function isDisposableEmail(email: string): boolean {
  if (typeof email !== "string") return false;
  const at = email.lastIndexOf("@");
  if (at < 0 || at === email.length - 1) return false;
  const domain = email.slice(at + 1).trim().toLowerCase();
  if (!domain) return false;
  if (DISPOSABLE_DOMAINS.has(domain)) return true;
  // Suffix walk for rotating-subdomain providers (foo.mailinator.com).
  const parts = domain.split(".");
  for (let i = 1; i < parts.length; i++) {
    const suffix = parts.slice(i).join(".");
    if (DISPOSABLE_DOMAINS.has(suffix)) return true;
  }
  return false;
}
