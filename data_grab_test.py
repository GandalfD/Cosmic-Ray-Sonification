from ftplib import FTP

ftp = FTP("ftp.ngdc.noaa.gov")
ftp.login()

ftp.cwd("/STP/SOLAR_DATA/COSMIC_RAYS/STATION_DATA/Calgary/docs/")
ftp.retrlines("RETR calgary.tab")

ftp.quit()
