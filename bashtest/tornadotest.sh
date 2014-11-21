#!/bin/bash

curl  http://localhost:64839 && echo " first done" &
curl  http://localhost:64839 && echo " second done" &
curl  http://localhost:64839 && echo " third done" &

wait

