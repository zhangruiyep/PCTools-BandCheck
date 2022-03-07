# AT BAND CHECK
 
History:
--------
* 2021/12/16 V1.6
	* 增加读OK重试次数，减少误测概率。

* 2021/12/16 V1.5
	* 修复BUG：写串口超时，工具报Exception，停止运行。
	
* 2021/12/16 V1.4
	* 设备数量改为1。
	* 自动选择ASR Modem Device端口。

* 2021/12/16 V1.3
	* 设备数量改为2。

* 2021/12/11 V1.2
	* 增加设备端口号重复检查，不允许设置相同的端口号
	
* 2021/12/11 V1.1
	* 修改了默认字体
	* 改进：当端口被其它软件占用，增加重试，直到端口可以打开
	
* 2021/12/11 V1.0
	* 需求：设备漏贴32K，导致在2G下死机。通过AT命令，将这部分故障机筛选出来。
	* 方案：AT*BAND=0, 设置为2G。之后连续给设备发送AT命令，检查设备是否可以正常响应。如果一段时间（15秒）内，出现USB掉口或者不响应，则为故障机。



