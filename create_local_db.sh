#!/bin/bash

psqluser="postgres"   # Database username
psqlpass="postgres"  # Database password
psqldb="jeugdzorg"   # Database name

{ # try

    psql -U postgres -d postgres -c "CREATE DATABASE $psqldb WITH OWNER $psqluser;"
    #command1 &&
    #save your output

} || { # catch
    echo "DB already created"
    # save log for exception
}
