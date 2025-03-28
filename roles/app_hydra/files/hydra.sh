#!/bin/bash
JAVA_PATH='/usr/lib/jvm/java-11-amazon-corretto/bin/java'
MY_PATH="/opt/bin/hydra"
MY_JAR="hydra.jar"
OPTS="-Xms3g -Xmx6g -XX:PermSize=256m -XX:MaxPermSize=1024m -XX:+UseG1GC"
cd $MY_PATH
if [ -f console.log ]
then
   mv console.log console.bak
fi
$JAVA_PATH $OPTS $TEMPOPTS -cp $MY_PATH/$MY_JAR:$MY_PATH -jar $MY_PATH/$MY_JAR &> console.log