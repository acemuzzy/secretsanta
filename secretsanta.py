# docopt
# pep8
# !bang

###########################
# Imports                 #
#  (email stuff, mainly)  #
###########################
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from datetime import date
import random

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
      print "Something's gone wrong!!!"
      exit(0)
   
    # Send away, using the email library
    msg = MIMEMultipart()

    ##################################
    # Change email details here...   #
    ##################################
    msg['From'] = "Santa Murray <a@b.c>" # @@ fill in sensibly
    msg['To'] = self.p1.email
    msg['Subject'] = "Your 2016 Secret Santa!!!" # @@ auto-date?
    body = """
    You, {}, have got to buy for {}!
    
    The budget is 50 pounds.

    Please note that I've generated this using a cunning computer program.
    So it may all have gone horribly wrong. Please get back to me if you have yourself or a spouse/other half!

    Also - WISHLISTS BY 31 OCTOBER PLEASE, so people have the chance to be organised early.  This also means
    you'll have forgotten your own list by the time Christmas arrives, so it'll be more surprising!

    Have fun :-)

    Murray (aka Secret Santa {}!)

    """.format(self.p1.name, self.p2.name, year)
    msg.attach(MIMEText(body, 'plain'))

    try:
       smtpObj = smtplib.SMTP('x.com') # @@ fill in sensibly
       smtpObj.sendmail(msg['From'], msg['To'],  msg.as_string())         
       print "Successfully sent email"
    except smtplib.SMTPException:
       print "Error: unable to send email"

###########################
# User config             #
###########################

# Define your contacts here.
# Make sure each has a unique name (the first parameter) # guarantee?
actual_santees = [Contact("a", "b@c.com"), #@@@ from file?
                  Contact("d", "e@f.com")]

trial_santees = [Contact(c.name, "g@h.com") for c in actual_santees]

santees = actual_santees

# Define any invalid pairs, e.g. spouses 
# Don't worry about (self,self) though, and you only need to do it one way round
invalid_pairs = [("Neil", "Claire"),
                 ("Murray", "Olivia"),
                 ("Julie", "Neill")]

###########################
# Brute force!            #
###########################

MAX_TRIES = 25
valid = True

###########################
# Seed random             #
###########################
random.seed()

# Keep looping - but have some cap in case it's impossible

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
    print "Success at %d" % attempt
    break

# OK, we either succeeded, or here the cap of attempts
if not valid:
  print "Failed to find a match in %d attempts - sorry!" % MAX_TRIES
  exit(0)

# OK, we have a valid set - send some emails!

with open(logging_file, "w") as f:
    for santer in range(0, len(santees)):
      email_pair = trial_pairs[santer]
      f.write("Pair {} -> {} (sent to {})\n".format(email_pair.p1.name, email_pair.p2.name, email_pair.p1.email))
      email_pair.SendEmail()
  

