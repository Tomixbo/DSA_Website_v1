# DSA_WEBSITE_V1
Repository for DSA INSI website v1 files.

The project is a website made with Django. The objective of the website is the management of coding challenges between the DSA's member and to monitor their performance.

## Features : 
- Managing challenges + levels + I/O files
- Testing user outputs
- Category and difficulty classement
- User account and profile
- User performance monitoring : score, rank, category

## Future implementations :
- Learning resources page
- Staff page : for adding/managing learning resources, challenges
- Making contest

## Deployment :
- verify the entrypoint.sh, and uncomment all needed command
- Launch all docker containers
> docker compose up -d
- open the url localhost in a browser
> http://localhost
- to access the website with another device in the same LAN : ip-address-of-pc-server (ex : 192.168.10.125) </br>
*Note : use the cmd command : "ipconfig -all" to see the ip-address

### Administration page :
Go to the next url for database administration :
> ip-address/admin
</br>
