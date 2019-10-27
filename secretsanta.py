"""
Secret Santa program - random allocation, with email, without bad pairings
"""

###########################
# Imports                 #
#  (email stuff, mainly)  #
###########################
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date
import random
import yaml

CONFIG_FILE = "mailconfig.yaml"

CONFIG_DEBUG_KEY = "debug"
CONFIG_SERVER_KEY = "server"
CONFIG_USERNAME_KEY = "user"
CONFIG_PASSWORD_KEY = "password"
CONFIG_SANTEES_KEY = "santees"
CONFIG_BANNED_PAIRINGS_KEY = "banned_pairings"

MAX_TRIES = 25

# Logging stuff
year = date.today().year
logging_file = "archive" + str(year) + ".txt"
print("Logging to {}".format(logging_file))


###########################
# Class for a contact     #
#  (name & email address) #
###########################
class Contact:
    def __init__(self, name, email):
        self.name = name
        self.email = email


###########################
# Class for a pairing     #
# p1 has to send to p2    #
###########################
class Pairing:

    # Constructor
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

    # Validity check - are they themselves or blacklisted?
    def Valid(self):
        for invalid_pair in invalid_pairs:
            if (((self.p1.name, self.p2.name) == invalid_pair) or
                    ((self.p2.name, self.p1.name) == invalid_pair) or
                    (self.p1.name == self.p2.name)):
                return False
        return True

    # Send an email.
    # This should only be done if valid!
    def SendEmail(self):
        if not self.Valid():
            # Oh dear, something's gone wrong!
            print("Something's gone wrong!!!")
            exit(0)

        # Send away, using the email library
        msg = MIMEMultipart()

        ##################################
        # Change email details here...   #
        ##################################
        msg['From'] = "Secret Santa <{}>".format(mail_username)
        msg['To'] = self.p1.email
        msg['Subject'] = "Your {} Secret Santa!!!".format(year)
        body = """
        You, {}, have got to buy for {}!

        The budget is 50 pounds.

        Please note that I've generated this using a cunning computer program.
        So it may all have gone horribly wrong. Please get back to me if you
        have yourself or a spouse/other half!

        Also - WISHLISTS BY 31 OCTOBER PLEASE, so people have the chance to be
        organised early.  This also means you'll have forgotten your own list
        by the time Christmas arrives, so it'll be more surprising!

        Have fun :-)

        Secret Santa {}!""".format(self.p1.name, self.p2.name, year)

        msg.attach(MIMEText(body, 'plain'))

        try:
            server = mail_server
            smtpObj = smtplib.SMTP(server, 587)
            smtpObj.login(mail_username, mail_password)
            smtpObj.sendmail(msg['From'], msg['To'], msg.as_string())
            print("Successfully sent email")
        except smtplib.SMTPException as e:
            print("Error: unable to send email: {}", e)


###########################
# User config             #
###########################
with open(CONFIG_FILE, 'r') as stream:
    mail_config = yaml.safe_load(stream)
    (mail_server, mail_username, mail_password) = \
        (mail_config[x] for x in [CONFIG_SERVER_KEY,
                                  CONFIG_USERNAME_KEY,
                                  CONFIG_PASSWORD_KEY])
    actual_santee_list = mail_config[CONFIG_SANTEES_KEY]
    banned_pairings = mail_config[CONFIG_BANNED_PAIRINGS_KEY]
    debug = mail_config.get(CONFIG_DEBUG_KEY, False)

# Check santees
actual_santees = []
for (name, email) in actual_santee_list.iteritems():
    actual_santees.append(Contact(name, email))

invalid_pairs = []
for (a, b) in banned_pairings.iteritems():
    if a not in actual_santee_list:
        print("Did not recognize {}".format(a))
        exit(1)
    if b not in actual_santee_list:
        print("Did not recognize {}".format(b))
        exit(1)
    invalid_pairs.append((a, b))

if debug:
    print("Debug mode - use single contact")
    trial_santees = [Contact(c.name, mail_username) for c in actual_santees]
    santees = trial_santees
else:
    print("Full mode")
    #santees = actual_santees
    pass

###########################
# Brute force!            #
###########################
random.seed()
valid = True
for attempt in range(0, MAX_TRIES):

    # Reset some local variables
    valid = True
    remaining_santees = santees[:]
    trial_pairs = []

    # Shuffle the list
    for santer in range(0, len(santees)):
        random_index = random.randint(0, len(remaining_santees) - 1)
        name = remaining_santees.pop(random_index)
        trial_pairs.append(Pairing(santees[santer], name))

    # Any breaches?  If not, we're done
    for santer in range(0, len(santees)):
        check_pair = trial_pairs[santer]
        if not check_pair.Valid():
            valid = False

    if valid:
        print("Success at %d" % attempt)
        break

# OK, we either succeeded, or here the cap of attempts
if not valid:
    print("Failed to find a match in %d attempts - sorry!" % MAX_TRIES)
    exit(0)

# OK, we have a valid set - send some emails!

with open(logging_file, "w") as f:
    for santer in range(0, len(santees)):
        email_pair = trial_pairs[santer]
        f.write("Pair {} -> {} (sent to {})\n".format(email_pair.p1.name,
                                                      email_pair.p2.name,
                                                      email_pair.p1.email))
        email_pair.SendEmail()

        if debug:
            break
