# Ben-Cookson-Github-License-Program
BYU OIT Software Developer position #82847

I wrote my code in Python (Version 3.7.0)
It it designed to be used in a terminal. I provided a bash script (install.sh) that installs all dependencies that aren't included in the python standard library.

The script is executed by the following command:
```
python create_license_pull_requests.py [organization] [username] [password]
```
If all 3 parameters are not passed in, the program will let the user know what parameters are expected and close. The progam does re-prompt the user for the parameter values if it is unable to authorize a request or find the desired organization. This isn't optimal for a scheduled process and could be changed, but **I am approaching this problem with the assumption that the user will be executing the code in person in the terminal.**

Rather than selecting a specific license per repository, I did some research and determined a MIT license was a good general license for BYU OIT repositories. That may be a wrong assumption, but I accounted for that in the pull request. Within the body of the pull request, I explain that I have chosen this particular license, but provide information and links for the user to select and apply a different license.

I provided more expansive error handling on the original authentication and request that gets a list of repositories. I took steps to try and succesfully make a request if the original request failed for some reason. With the later API calls for each individual Repository, I didn't do any handling for a timed out request other than notifying the user. I don't know what kind of error handling is custom for BYU OIT, but my code could be modified to log errors in an external file, or email someone when a process fails. To the best of my knowledge, no error should go unhandled, but any unexpected errors will result.

##Here are some other assumptions that i am working under:
*The repository must have a master branch (Though I can't think of a case this wouldn't be true)
*Private and Public repositories respond the same (My free organization I tested on didn't have the ability to create private repos)

