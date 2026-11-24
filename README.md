##SeungHwan CHEON
#use MBC module and STM32F103C8Tx board(you can check in .ioc), nodeMCU-MQTT-Mosdquitto, ST-Debuger(not OPEN OCD)

###########################################################################
1. database-mySQL0.8 is stored by spring Hibernate that insert into temp_log(calum) 
**Hibernate: insert into temp_log (created_at,device_id,value) values (?,?,?)
2026-11-24T17:08:12.021+09:00  INFO 16344 --- [: spring-server] c.i.firstimbeter.config.MqttSubscriber   : saved lab/node1/temp = 25.8
Hibernate: insert into temp_log (created_at,device_id,value) values (?,?,?)
2026-11-24T17:08:21.766+09:00  INFO 16344 --- [: spring-server] c.i.firstimbeter.config.MqttSubscriber   : saved lab/node3/temp = 100.0
Hibernate: insert into temp_log (created_at,device_id,value) values (?,?,?)
2026-11-24T17:08:25.615+09:00  INFO 16344 --- [: spring-server] c.i.firstimbeter.config.MqttSubscriber   : saved lab/node3/temp = 67.0**

opencode plugin add github:vercel/vercel-plugin

##END SeungHwan CHEON addition
