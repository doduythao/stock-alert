# stock-alert

This script would run by crontab (or task scheduler on Windows) from 9:00 to 15:00 (Vietnam stock exchange working session) to check price and alert by rules on stock_list file

Install beautifulsoup

Install & run splash server at port 8050 (recommmend use docker to install, easiest way, make sure the splash running after close docker command windows and running before 9:00 everyday)

Prepare a gmail account, remember to create application password! (don't use normal password because Google doesn't allow to send mail with normal password by email package)
