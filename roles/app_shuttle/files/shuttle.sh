#!/bin/bash
#JAVA_PATH='/usr/lib/jvm/java-8-oracle/jre/bin/java'
JAVA_PATH='/usr/lib/jvm/java-11-openjdk-amd64/bin/java'
MY_PATH="/opt/bin/shuttle"
MY_JAR="shuttleApp.jar"
# OPTS="-Xms2g -Xmx3g -XX:MaxPermSize=640m -server -Dhttps.protocols=TLSv1,TLSv1.1,TLSv1.2"
# OPTS="-Dspring.config.location=$MY_PATH/application.yml -Dlogging.config=$MY_PATH/logback.groovy"
cd $MY_PATH
if [ -f console.log ]
then
   mv console.log console.bak
fi
$JAVA_PATH $OPTS -cp $MY_PATH/$MY_JAR:$MY_PATH -jar $MY_PATH/$MY_JAR &> console.log