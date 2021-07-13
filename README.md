# Ebay-Kleinanzeigen-telegram
Mini bot that allows to check out the new Anzeigen without making too many requests, as it has a parameter of minimum time between requests, and cycles between the different given URLs so that there is a balance.

How to use it

1-Install in your python environment bs4 and telegram, maybe with pip install
2-Create a bot in the telegram app with the @BotFather, and save the token in either a file or somewhere. You can input the token in the command line or referencing the file.
3-Create a file with all the URL that you want to check in Ebay-Kleinanzeigen after you search for something, it will check out the list that you would see normaly after clicking on search. You can pass the url manually or with the mentioned file.
4-Set the minimum and maximum time before making a new request

Examples:
python "observer-kleinanzeigen.py" -tf token.txt -uf url.txt -mins 300 -maxs 600 

-t : token as text
-tf : name of the file with the token
-u : url to be observed
-uf : file with the urls to be observed

-mins : minimum time before a new request
-maxs : maximum time before new request
The request will be done with a random number between these two limits, in seconds

To start write /start
