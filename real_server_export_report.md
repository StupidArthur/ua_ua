# Real OPC UA Server 地址空间导出报告

## 1. 基本信息

- 连接地址: `opc.tcp://10.10.58.117:18639`
- 导出时间: `2026-07-21T03:04:53.356162+00:00`
- ApplicationName: `NeuroShellForCMS Server` (locale=`en-US`)
- ApplicationUri: `http://SUPCON.UAServer.Application`
- ProductUri: `http://www.supcon.com`
- ApplicationType: `Server`
- GatewayServerUri: `None`
- DiscoveryProfileUri: `None`
- ServerArray: `['http://SUPCON.UAServer.Application']`
- ServerStatus.State: `Running`
- ServerStatus.StartTime: `2026-07-15T05:44:34.539000+00:00`
- ServerStatus.CurrentTime: `2026-07-21T03:02:39.142000+00:00`
- BuildInfo.ProductUri: `http://www.supcon.com`
- BuildInfo.ManufacturerName: `SUPCON`
- BuildInfo.ProductName: `SUPCON OPC UA Server`
- BuildInfo.SoftwareVersion: `1.2.2-unknown`
- BuildInfo.BuildNumber: `Dec  6 2024 09:20:23`
- BuildInfo.BuildDate: `2026-07-15T05:44:34.538000+00:00`

### NamespaceArray

| Index | URI |
|------:|-----|
| 0 | `http://opcfoundation.org/UA/` |
| 1 | `http://SUPCON.UAServer.Product` |
| 2 | `http://supcon.com/UA` |
| 3 | `http://opcfoundation.org/UA/Dictionary/IRDI` |
| 4 | `http://opcfoundation.org/UA/DI/` |
| 5 | `http://opcfoundation.org/UA/PADIM/` |
| 6 | `http://www.OPCFoundation.org/UA/2013/01/ISA95` |

### 采集数量

- 实例节点数量: **414**
- 类型节点数量: **737**
- 引用数量: **13467**
- Object 节点: **184**
- Variable 节点: **892**
- Method 节点: **12**
- ObjectType 节点: **44**
- VariableType 节点: **19**
- DataType 节点: **0**
- ReferenceType 节点: **0**
- 错误数量: **0**
- 找到的设备: `SOV1, SOV2, SOV3, SOV4, SOV5, SOV6, SOV7, SOV8`

## 2. 根结构（实例树）

```
Objects  (Object)  [i=85]
   ├─ DeviceSet  (Object)  [ns=4;i=5001]
   │  └─ DeviceFeatures  (Object)  [ns=4;i=15034]
   ├─ DeviceSetView  (Object)  [ns=2;s=P_7765a8f78a9266d7a83581ba1b39176a]
   │  ├─ SOV1  (Object)  [ns=1;s=7c8af738ba72d0e9226c57c70ab0310d_ch1]
   │  │  ├─ AssetId  (Variable)  [ns=4;s=P_318b26d74fcca15eeb08a56d2f1b6f3a]
   │  │  ├─ Configuration  (Object)  [ns=1;s=P_0f82c9b911a44bc3a4185b1fe83be125]
   │  │  │  ├─ CurrentType  (Variable)  [ns=1;s=P_cdc75745a8441147e448e8f845243c64]
   │  │  │  └─ SnapshotPeriod  (Variable)  [ns=1;s=P_c4e95c9b3819dd8bb1f24ca02b5127b6]
   │  │  ├─ DeviceClass  (Variable)  [ns=1;s=P_10384fe20b16c81537f93e40558636e6]
   │  │  └─ Runtime  (Object)  [ns=1;s=P_cadfd5973419d77015b9410f9ceda34e]
   │  │     ├─ ActionSnapshot  (Variable)  [ns=1;s=P_3c9fcf915366945544cd1b4032d0afe0]
   │  │     ├─ Current  (Variable)  [ns=1;s=P_fb349055a732ddf6511d1367e07bf492]
   │  │     │  └─ EURange  (Variable)  [ns=0;s=P_d96e61438d6080321565c5718839603d]
   │  │     ├─ FaultState  (Variable)  [ns=1;s=P_79d0616e3e1a8613be1456bd90f5e544]
   │  │     │  └─ TypeMismatch  (Variable)  [ns=1;s=P_cb0a950cc7e57148a93bd1d6027a720c]
   │  │     └─ OnlineState  (Variable)  [ns=1;s=P_0fd57de4b78346a354e7f8725d4cd95f]
   │  ├─ SOV2  (Object)  [ns=1;s=7c8af738ba72d0e9226c57c70ab0310d_ch2]
   │  │  ├─ AssetId  (Variable)  [ns=4;s=P_16a829974831930e47043de7b80d8457]
   │  │  ├─ Configuration  (Object)  [ns=1;s=P_3c15dcca6d48d74363386cad305684bd]
   │  │  │  ├─ CurrentType  (Variable)  [ns=1;s=P_fd5259a831abe0a5ba9a188f6a9e3f14]
   │  │  │  └─ SnapshotPeriod  (Variable)  [ns=1;s=P_b6290506efddb6aeb7eb2a4250f5456f]
   │  │  ├─ DeviceClass  (Variable)  [ns=1;s=P_4938367246db2047b9e18773dcd8a6da]
   │  │  └─ Runtime  (Object)  [ns=1;s=P_6e216f654e8df0109fd559133e230fe4]
   │  │     ├─ ActionSnapshot  (Variable)  [ns=1;s=P_0176568ccf8d6094d634200d664aad42]
   │  │     ├─ Current  (Variable)  [ns=1;s=P_fd55af1df94de2810bb75b396833f6d1]
   │  │     │  └─ EURange  (Variable)  [ns=0;s=P_df8e9f31521e4a425d4cfc069e9a167e]
   │  │     ├─ FaultState  (Variable)  [ns=1;s=P_95f9d94fd5622e5a0aefb9d14415721d]
   │  │     │  └─ TypeMismatch  (Variable)  [ns=1;s=P_cb976c6a706152499dd2c4309acd95a2]
   │  │     └─ OnlineState  (Variable)  [ns=1;s=P_cf562a5a86461acfaf8b43700c224351]
   │  ├─ SOV3  (Object)  [ns=1;s=7c8af738ba72d0e9226c57c70ab0310d_ch3]
   │  │  ├─ AssetId  (Variable)  [ns=4;s=P_28dde1842eb938237d79a59b4381bde1]
   │  │  ├─ Configuration  (Object)  [ns=1;s=P_5e4c31e145c0f80c8cef50263f86edad]
   │  │  │  ├─ CurrentType  (Variable)  [ns=1;s=P_995d145ac10eb739033fb5d3b7a74ec9]
   │  │  │  └─ SnapshotPeriod  (Variable)  [ns=1;s=P_ee2e9b41ea79c938b572ef063d7a2327]
   │  │  ├─ DeviceClass  (Variable)  [ns=1;s=P_9794aadb8074e2d77783f7086b15982c]
   │  │  └─ Runtime  (Object)  [ns=1;s=P_48a91d6d54bd31590b96e8b98d8e75a3]
   │  │     ├─ ActionSnapshot  (Variable)  [ns=1;s=P_72f0ba7933fd59393cba4ed167da76a2]
   │  │     ├─ Current  (Variable)  [ns=1;s=P_264c303711ef2d01f43489e1afdb19a2]
   │  │     │  └─ EURange  (Variable)  [ns=0;s=P_07495a943ab99e742a21e2b7654ee962]
   │  │     ├─ FaultState  (Variable)  [ns=1;s=P_29495a285f5b162a4a36d009e8a129c9]
   │  │     │  └─ TypeMismatch  (Variable)  [ns=1;s=P_2e226206224e7a2f0f0edc155b8c30ef]
   │  │     └─ OnlineState  (Variable)  [ns=1;s=P_2f21f8471209f4389f215bf3cacc4e50]
   │  ├─ SOV4  (Object)  [ns=1;s=7c8af738ba72d0e9226c57c70ab0310d_ch4]
   │  │  ├─ AssetId  (Variable)  [ns=4;s=P_dc67c5ec23bff00b663d28bcbba78716]
   │  │  ├─ Configuration  (Object)  [ns=1;s=P_009cdfb397e90ffb1c7d9c3e16b3c57c]
   │  │  │  ├─ CurrentType  (Variable)  [ns=1;s=P_567b992d8552e4281c39d404cde055df]
   │  │  │  └─ SnapshotPeriod  (Variable)  [ns=1;s=P_698e6817db426c01b58e1318706f62ac]
   │  │  ├─ DeviceClass  (Variable)  [ns=1;s=P_314066c01deddc24e92182d2ccb589a4]
   │  │  └─ Runtime  (Object)  [ns=1;s=P_a242b43221b57107bc78119f8fdf0a81]
   │  │     ├─ ActionSnapshot  (Variable)  [ns=1;s=P_7bced210db53cae0cdebd4492ae525c6]
   │  │     ├─ Current  (Variable)  [ns=1;s=P_9464963d95cf68daf788be3817f7f471]
   │  │     │  └─ EURange  (Variable)  [ns=0;s=P_49e341430055fbf66a5826ba64db60e3]
   │  │     ├─ FaultState  (Variable)  [ns=1;s=P_c8a9a7a8a89242cda928ebeb03b84fb8]
   │  │     │  └─ TypeMismatch  (Variable)  [ns=1;s=P_6373d648077997fd3c88bf73608ddd4a]
   │  │     └─ OnlineState  (Variable)  [ns=1;s=P_56e7ff2f301c44bdbfab109e03aff22d]
   │  ├─ SOV5  (Object)  [ns=1;s=7c8af738ba72d0e9226c57c70ab0310d_ch5]
   │  │  ├─ AssetId  (Variable)  [ns=4;s=P_b1941dec912588efe46b20883a6fe2be]
   │  │  ├─ Configuration  (Object)  [ns=1;s=P_421b6df61324737922a15bf41283038f]
   │  │  │  ├─ CurrentType  (Variable)  [ns=1;s=P_371b2ebfa6af199c2d221a1155512b1a]
   │  │  │  └─ SnapshotPeriod  (Variable)  [ns=1;s=P_65d9a4f93d611affccba5e3e24910b65]
   │  │  ├─ DeviceClass  (Variable)  [ns=1;s=P_c87eca1ac0a1896c9b4b35eb8184973e]
   │  │  └─ Runtime  (Object)  [ns=1;s=P_8c1da3d4a7b1bca51a71452b7945d0eb]
   │  │     ├─ ActionSnapshot  (Variable)  [ns=1;s=P_ed47682ac8f276c2ec3f364b68dbdffd]
   │  │     ├─ Current  (Variable)  [ns=1;s=P_d19f54c0004c905e230f0aa1c0a23212]
   │  │     │  └─ EURange  (Variable)  [ns=0;s=P_cab087b64f081de5f8836b36813784df]
   │  │     ├─ FaultState  (Variable)  [ns=1;s=P_ef451d6199229d4662149a3bf9b416eb]
   │  │     │  └─ TypeMismatch  (Variable)  [ns=1;s=P_f5f180a8a2df359ab406d6c51d6cf1d0]
   │  │     └─ OnlineState  (Variable)  [ns=1;s=P_319215b4acff4f3d8b34a04ae432bb0d]
   │  ├─ SOV6  (Object)  [ns=1;s=7c8af738ba72d0e9226c57c70ab0310d_ch6]
   │  │  ├─ AssetId  (Variable)  [ns=4;s=P_9cc79e53a8f708b517461d71efea877e]
   │  │  ├─ Configuration  (Object)  [ns=1;s=P_1b1bd8de019344d2bc887a762d3a9e72]
   │  │  │  ├─ CurrentType  (Variable)  [ns=1;s=P_eb3514fbb09f9a29745846f5bff6b4e2]
   │  │  │  └─ SnapshotPeriod  (Variable)  [ns=1;s=P_b6b309f15ba1f40790d563eae089894e]
   │  │  ├─ DeviceClass  (Variable)  [ns=1;s=P_5028974dfbba4c963e5ce231c9b830a0]
   │  │  └─ Runtime  (Object)  [ns=1;s=P_59dad4e4a142bb938923fc9da20125f6]
   │  │     ├─ ActionSnapshot  (Variable)  [ns=1;s=P_baa5c6aae99ec39d87c901a488cf3805]
   │  │     ├─ Current  (Variable)  [ns=1;s=P_a8df71d63ea6afe4c8c455640a2d26ae]
   │  │     │  └─ EURange  (Variable)  [ns=0;s=P_1175f5b7f7990e21f6ed1c27bd5e9192]
   │  │     ├─ FaultState  (Variable)  [ns=1;s=P_ef5e9e9fcfb98a8905a647a3a920e633]
   │  │     │  └─ TypeMismatch  (Variable)  [ns=1;s=P_ced29318494832827ea70444ae11f3db]
   │  │     └─ OnlineState  (Variable)  [ns=1;s=P_75d36fb750e11e393497a2c7200c78d0]
   │  ├─ SOV7  (Object)  [ns=1;s=7c8af738ba72d0e9226c57c70ab0310d_ch7]
   │  │  ├─ AssetId  (Variable)  [ns=4;s=P_d6e8b80e832297c58597599842b65b7c]
   │  │  ├─ Configuration  (Object)  [ns=1;s=P_fabc48adb6d0de562b88e1f5a0182df3]
   │  │  │  ├─ CurrentType  (Variable)  [ns=1;s=P_d0e8a17cb2261468891112112d97e0a0]
   │  │  │  └─ SnapshotPeriod  (Variable)  [ns=1;s=P_9388e6a7ad75f1fcf5de12850e765a4c]
   │  │  ├─ DeviceClass  (Variable)  [ns=1;s=P_fc43f4ae11cb496fbc03e8be71265786]
   │  │  └─ Runtime  (Object)  [ns=1;s=P_2c621643996d062c5585ff9cfa50e55f]
   │  │     ├─ ActionSnapshot  (Variable)  [ns=1;s=P_02dc0cca86cd00b5b830db7616757a10]
   │  │     ├─ Current  (Variable)  [ns=1;s=P_519db2a64cb7a0f0b9d703da51de5cbb]
   │  │     │  └─ EURange  (Variable)  [ns=0;s=P_524770cf890db78b319175318ea11ad8]
   │  │     ├─ FaultState  (Variable)  [ns=1;s=P_d803d26cc24a1d33340b0054b4737653]
   │  │     │  └─ TypeMismatch  (Variable)  [ns=1;s=P_f5453190c79e7a4a8000bfa7dff95582]
   │  │     └─ OnlineState  (Variable)  [ns=1;s=P_d0dd9e5cf1a67686ffaf51cb013edd3f]
   │  └─ SOV8  (Object)  [ns=1;s=7c8af738ba72d0e9226c57c70ab0310d_ch8]
   │     ├─ AssetId  (Variable)  [ns=4;s=P_f7effec354409e6f575b020417fabef8]
   │     ├─ Configuration  (Object)  [ns=1;s=P_49eb2e53ae2299e5ee34333cfa013512]
   │     │  ├─ CurrentType  (Variable)  [ns=1;s=P_d812a687c56f5f6ebd9b81b6e8f6786a]
   │     │  └─ SnapshotPeriod  (Variable)  [ns=1;s=P_71fb79d8831dd100d81216367f119a0a]
   │     ├─ DeviceClass  (Variable)  [ns=1;s=P_3c26385c96e52a57d6ac55cde11a2cb7]
   │     └─ Runtime  (Object)  [ns=1;s=P_8cc2abe6bee8c358f6c3cbcf2193b557]
   │        ├─ ActionSnapshot  (Variable)  [ns=1;s=P_f317c48a74664fe450f0eacf2ca4770c]
   │        ├─ Current  (Variable)  [ns=1;s=P_3bb8aeba5dce893483972314cc4ad2f0]
   │        │  └─ EURange  (Variable)  [ns=0;s=P_65831eeacd89eb84df62aad1c433b101]
   │        ├─ FaultState  (Variable)  [ns=1;s=P_accd99608ad98f1ea7e076917003ab12]
   │        │  └─ TypeMismatch  (Variable)  [ns=1;s=P_60766f4218185993005470d12a5c6b5a]
   │        └─ OnlineState  (Variable)  [ns=1;s=P_24a08d31e438ed63fedb5f46538c03d6]
   ├─ DeviceTopology  (Object)  [ns=4;i=6094]
   │  └─ OnlineAccess  (Variable)  [ns=4;i=6095]
   ├─ EquipmentModel  (Object)  [ns=2;i=5044]
   └─ NetworkSet  (Object)  [ns=4;i=6078]
Aliases  (Object)  [ns=0;i=23470]
Topics  (Object)  [ns=0;i=23488]
FindAlias  (Method)  [ns=0;i=23494]
OutputArguments  (Variable)  [ns=0;i=23496]
InputArguments  (Variable)  [ns=0;i=23495]
TagVariables  (Object)  [ns=0;i=23479]
FindAlias  (Method)  [ns=0;i=23485]
OutputArguments  (Variable)  [ns=0;i=23487]
InputArguments  (Variable)  [ns=0;i=23486]
FindAlias  (Method)  [ns=0;i=23476]
OutputArguments  (Variable)  [ns=0;i=23478]
InputArguments  (Variable)  [ns=0;i=23477]
Server  (Object)  [ns=0;i=2253]
   ├─ ModelChangeNode  (Object)  [ns=0;i=3907086]
   │  ├─ Changes  (Variable)  [ns=0;i=15303965]
   │  ├─ EventId  (Variable)  [ns=0;i=1661764]
   │  ├─ EventType  (Variable)  [ns=0;i=5975562]
   │  ├─ Message  (Variable)  [ns=0;i=7387932]
   │  ├─ ReceiveTime  (Variable)  [ns=0;i=2043469]
   │  ├─ Severity  (Variable)  [ns=0;i=4833094]
   │  ├─ SourceName  (Variable)  [ns=0;i=9917426]
   │  ├─ SourceNode  (Variable)  [ns=0;i=11346424]
   │  └─ Time  (Variable)  [ns=0;i=11706481]
   └─ RestartShell  (Method)  [ns=4;s=method_restart_server]
      └─ OutputArguments  (Variable)  [ns=0;s=P_69a6fe38325a94c68e2afd0ef39640e7]
Auditing  (Variable)  [ns=0;i=2994]
ServiceLevel  (Variable)  [ns=0;i=2267]
ServerArray  (Variable)  [ns=0;i=2254]
NamespaceArray  (Variable)  [ns=0;i=2255]
Resources  (Object)  [ns=0;i=24226]
Communication  (Object)  [ns=0;i=24227]
NetworkInterfaces  (Object)  [ns=0;i=24229]
Streams  (Object)  [ns=0;i=24230]
ListenerStreams  (Object)  [ns=0;i=24232]
TalkerStreams  (Object)  [ns=0;i=24231]
MappingTables  (Object)  [ns=0;i=24228]
VendorServerInfo  (Object)  [ns=0;i=2295]
ServerDiagnostics  (Object)  [ns=0;i=2274]
EnabledFlag  (Variable)  [ns=0;i=2294]
SessionsDiagnosticsSummary  (Object)  [ns=0;i=3706]
SessionDiagnosticsArray  (Variable)  [ns=0;i=3707]
SessionSecurityDiagnosticsArray  (Variable)  [ns=0;i=3708]
SamplingIntervalDiagnosticsArray  (Variable)  [ns=0;i=2289]
SubscriptionDiagnosticsArray  (Variable)  [ns=0;i=2290]
ServerDiagnosticsSummary  (Variable)  [ns=0;i=2275]
   ├─ HostCpuLoad  (Variable)  [ns=4;s=P_72a7e104f87c0ac3c07ca31b526e138f]
   ├─ HostName  (Variable)  [ns=4;s=P_ae6bc00b4a48bc099820cb5ba7581827]
   └─ HostRAMLoad  (Variable)  [ns=4;s=P_550508a99e4f8ebb9feaeb9f6cf0820a]
CumulatedSubscriptionCount  (Variable)  [ns=0;i=2286]
PublishingIntervalCount  (Variable)  [ns=0;i=2284]
SecurityRejectedSessionCount  (Variable)  [ns=0;i=2279]
CurrentSubscriptionCount  (Variable)  [ns=0;i=2285]
RejectedRequestsCount  (Variable)  [ns=0;i=2288]
CumulatedSessionCount  (Variable)  [ns=0;i=2278]
RejectedSessionCount  (Variable)  [ns=0;i=3705]
SessionAbortCount  (Variable)  [ns=0;i=2282]
SessionTimeoutCount  (Variable)  [ns=0;i=2281]
ServerViewCount  (Variable)  [ns=0;i=2276]
CurrentSessionCount  (Variable)  [ns=0;i=2277]
SecurityRejectedRequestsCount  (Variable)  [ns=0;i=2287]
ServerRedundancy  (Object)  [ns=0;i=2296]
RedundancySupport  (Variable)  [ns=0;i=3709]
ServerCapabilities  (Object)  [ns=0;i=2268]
   └─ MaxInactiveLockTime  (Variable)  [ns=4;i=6387]
MaxHistoryContinuationPoints  (Variable)  [ns=0;i=2737]
MaxBrowseContinuationPoints  (Variable)  [ns=0;i=2735]
SoftwareCertificates  (Variable)  [ns=0;i=3704]
MinSupportedSampleRate  (Variable)  [ns=0;i=2272]
LocaleIdArray  (Variable)  [ns=0;i=2271]
MaxQueryContinuationPoints  (Variable)  [ns=0;i=2736]
ServerProfileArray  (Variable)  [ns=0;i=2269]
AggregateFunctions  (Object)  [ns=0;i=2997]
ModellingRules  (Object)  [ns=0;i=2996]
ExposesItsArray  (Object)  [ns=0;i=83]
NamingRule  (Variable)  [ns=0;i=114]
Mandatory  (Object)  [ns=0;i=78]
NamingRule  (Variable)  [ns=0;i=112]
OptionalPlaceholder  (Object)  [ns=0;i=11508]
NamingRule  (Variable)  [ns=0;i=11509]
Optional  (Object)  [ns=0;i=80]
NamingRule  (Variable)  [ns=0;i=113]
MandatoryPlaceholder  (Object)  [ns=0;i=11510]
NamingRule  (Variable)  [ns=0;i=11511]
HistoryServerCapabilities  (Object)  [ns=0;i=11192]
AccessHistoryDataCapability  (Variable)  [ns=0;i=11193]
ServerTimestampSupported  (Variable)  [ns=0;i=19091]
ReplaceEventCapability  (Variable)  [ns=0;i=11282]
MaxReturnDataValues  (Variable)  [ns=0;i=11273]
InsertEventCapability  (Variable)  [ns=0;i=11281]
UpdateDataCapability  (Variable)  [ns=0;i=11198]
MaxReturnEventValues  (Variable)  [ns=0;i=11274]
AccessHistoryEventsCapability  (Variable)  [ns=0;i=11242]
InsertAnnotationCapability  (Variable)  [ns=0;i=11275]
UpdateEventCapability  (Variable)  [ns=0;i=11283]
DeleteAtTimeCapability  (Variable)  [ns=0;i=11200]
DeleteRawCapability  (Variable)  [ns=0;i=11199]
ReplaceDataCapability  (Variable)  [ns=0;i=11197]
InsertDataCapability  (Variable)  [ns=0;i=11196]
DeleteEventCapability  (Variable)  [ns=0;i=11502]
AggregateFunctions  (Object)  [ns=0;i=11201]
OperationLimits  (Object)  [ns=0;i=11704]
MaxNodesPerWrite  (Variable)  [ns=0;i=11707]
MaxNodesPerNodeManagement  (Variable)  [ns=0;i=11713]
MaxNodesPerRegisterNodes  (Variable)  [ns=0;i=11711]
MaxNodesPerRead  (Variable)  [ns=0;i=11705]
MaxNodesPerTranslateBrowsePathsToNodeIds  (Variable)  [ns=0;i=11712]
MaxNodesPerBrowse  (Variable)  [ns=0;i=11710]
MaxNodesPerMethodCall  (Variable)  [ns=0;i=11709]
MaxMonitoredItemsPerCall  (Variable)  [ns=0;i=11714]
ServerStatus  (Variable)  [ns=0;i=2256]
BuildInfo  (Variable)  [ns=0;i=2260]
   └─ InstanceName  (Variable)  [ns=4;s=P_433fc2c5fe82706172d6e87bfae1b35a]
BuildDate  (Variable)  [ns=0;i=2266]
SoftwareVersion  (Variable)  [ns=0;i=2264]
ProductUri  (Variable)  [ns=0;i=2262]
ProductName  (Variable)  [ns=0;i=2261]
ManufacturerName  (Variable)  [ns=0;i=2263]
BuildNumber  (Variable)  [ns=0;i=2265]
ShutdownReason  (Variable)  [ns=0;i=2993]
SecondsTillShutdown  (Variable)  [ns=0;i=2992]
CurrentTime  (Variable)  [ns=0;i=2258]
State  (Variable)  [ns=0;i=2259]
StartTime  (Variable)  [ns=0;i=2257]
Dictionaries  (Object)  [ns=0;i=17594]
   ├─ 0112/2///61987#ABA038#003  (Object)  [ns=3;s=0112/2///61987#ABA038#003]
   ├─ 0112/2///61987#ABA300#006  (Object)  [ns=3;s=0112/2///61987#ABA300#006]
   ├─ 0112/2///61987#ABA418#001  (Object)  [ns=3;s=0112/2///61987#ABA418#001]
   ├─ 0112/2///61987#ABA565#007  (Object)  [ns=3;s=0112/2///61987#ABA565#007]
   ├─ 0112/2///61987#ABA567#007  (Object)  [ns=3;s=0112/2///61987#ABA567#007]
   ├─ 0112/2///61987#ABA601#006  (Object)  [ns=3;s=0112/2///61987#ABA601#006]
   ├─ 0112/2///61987#ABA635#002  (Object)  [ns=3;s=0112/2///61987#ABA635#002]
   ├─ 0112/2///61987#ABA926#006  (Object)  [ns=3;s=0112/2///61987#ABA926#006]
   ├─ 0112/2///61987#ABA927#005  (Object)  [ns=3;s=0112/2///61987#ABA927#005]
   ├─ 0112/2///61987#ABA946#004  (Object)  [ns=3;s=0112/2///61987#ABA946#004]
   ├─ 0112/2///61987#ABA951#007  (Object)  [ns=3;s=0112/2///61987#ABA951#007]
   ├─ 0112/2///61987#ABA968#002  (Object)  [ns=3;s=0112/2///61987#ABA968#002]
   ├─ 0112/2///61987#ABB088#002  (Object)  [ns=3;s=0112/2///61987#ABB088#002]
   ├─ 0112/2///61987#ABB091#002  (Object)  [ns=3;s=0112/2///61987#ABB091#002]
   ├─ 0112/2///61987#ABB092#002  (Object)  [ns=3;s=0112/2///61987#ABB092#002]
   ├─ 0112/2///61987#ABB093#002  (Object)  [ns=3;s=0112/2///61987#ABB093#002]
   ├─ 0112/2///61987#ABB271#007  (Object)  [ns=3;s=0112/2///61987#ABB271#007]
   ├─ 0112/2///61987#ABB290#005  (Object)  [ns=3;s=0112/2///61987#ABB290#005]
   ├─ 0112/2///61987#ABB291#005  (Object)  [ns=3;s=0112/2///61987#ABB291#005]
   ├─ 0112/2///61987#ABB292#005  (Object)  [ns=3;s=0112/2///61987#ABB292#005]
   ├─ 0112/2///61987#ABD740#002  (Object)  [ns=3;s=0112/2///61987#ABD740#002]
   ├─ 0112/2///61987#ABD742#002  (Object)  [ns=3;s=0112/2///61987#ABD742#002]
   ├─ 0112/2///61987#ABE882#001  (Object)  [ns=3;s=0112/2///61987#ABE882#001]
   ├─ 0112/2///61987#ABH327#001  (Object)  [ns=3;s=0112/2///61987#ABH327#001]
   ├─ 0112/2///61987#ABH328#001  (Object)  [ns=3;s=0112/2///61987#ABH328#001]
   ├─ 0112/2///61987#ABH329#002  (Object)  [ns=3;s=0112/2///61987#ABH329#002]
   ├─ 0112/2///61987#ABH526#002  (Object)  [ns=3;s=0112/2///61987#ABH526#002]
   ├─ 0112/2///61987#ABJ683#001  (Object)  [ns=3;s=0112/2///61987#ABJ683#001]
   ├─ 0112/2///61987#ABJ724#002  (Object)  [ns=3;s=0112/2///61987#ABJ724#002]
   ├─ 0112/2///61987#ABN590#001  (Object)  [ns=3;s=0112/2///61987#ABN590#001]
   ├─ 0112/2///61987#ABN591#001  (Object)  [ns=3;s=0112/2///61987#ABN591#001]
   ├─ 0112/2///61987#ABN594#002  (Object)  [ns=3;s=0112/2///61987#ABN594#002]
   ├─ 0112/2///61987#ABN597#001  (Object)  [ns=3;s=0112/2///61987#ABN597#001]
   ├─ 0112/2///61987#ABN603#001  (Object)  [ns=3;s=0112/2///61987#ABN603#001]
   ├─ 0112/2///61987#ABN604#001  (Object)  [ns=3;s=0112/2///61987#ABN604#001]
   ├─ 0112/2///61987#ABN607#001  (Object)  [ns=3;s=0112/2///61987#ABN607#001]
   ├─ 0112/2///61987#ABN609#001  (Object)  [ns=3;s=0112/2///61987#ABN609#001]
   ├─ 0112/2///61987#ABN611#001  (Object)  [ns=3;s=0112/2///61987#ABN611#001]
   ├─ 0112/2///61987#ABN613#001  (Object)  [ns=3;s=0112/2///61987#ABN613#001]
   ├─ 0112/2///61987#ABN614#001  (Object)  [ns=3;s=0112/2///61987#ABN614#001]
   ├─ 0112/2///61987#ABN616#001  (Object)  [ns=3;s=0112/2///61987#ABN616#001]
   ├─ 0112/2///61987#ABN632#001  (Object)  [ns=3;s=0112/2///61987#ABN632#001]
   ├─ 0112/2///61987#ABN634#001  (Object)  [ns=3;s=0112/2///61987#ABN634#001]
   ├─ 0112/2///61987#ABN635#001  (Object)  [ns=3;s=0112/2///61987#ABN635#001]
   ├─ 0112/2///61987#ABN636#001  (Object)  [ns=3;s=0112/2///61987#ABN636#001]
   ├─ 0112/2///61987#ABN637#001  (Object)  [ns=3;s=0112/2///61987#ABN637#001]
   ├─ 0112/2///61987#ABN644#001  (Object)  [ns=3;s=0112/2///61987#ABN644#001]
   ├─ 0112/2///61987#ABN645#001  (Object)  [ns=3;s=0112/2///61987#ABN645#001]
   ├─ 0112/2///61987#ABN646#001  (Object)  [ns=3;s=0112/2///61987#ABN646#001]
   ├─ 0112/2///61987#ABN726#001  (Object)  [ns=3;s=0112/2///61987#ABN726#001]
   └─ 0112/2///61987#ABN972#001  (Object)  [ns=3;s=0112/2///61987#ABN972#001]
PublishSubscribe  (Object)  [ns=0;i=14443]
SupportedTransportProfiles  (Variable)  [ns=0;i=17481]
RemoveConnection  (Method)  [ns=0;i=17369]
InputArguments  (Variable)  [ns=0;i=17370]
GetSecurityKeys  (Method)  [ns=0;i=15215]
OutputArguments  (Variable)  [ns=0;i=15217]
InputArguments  (Variable)  [ns=0;i=15216]
AddConnection  (Method)  [ns=0;i=17366]
InputArguments  (Variable)  [ns=0;i=17367]
OutputArguments  (Variable)  [ns=0;i=17368]
GetSecurityGroup  (Method)  [ns=0;i=15440]
OutputArguments  (Variable)  [ns=0;i=15442]
InputArguments  (Variable)  [ns=0;i=15441]
Diagnostics  (Object)  [ns=0;i=17409]
TotalInformation  (Variable)  [ns=0;i=17411]
DiagnosticsLevel  (Variable)  [ns=0;i=17414]
Classification  (Variable)  [ns=0;i=17413]
Active  (Variable)  [ns=0;i=17412]
TotalError  (Variable)  [ns=0;i=17416]
Classification  (Variable)  [ns=0;i=17418]
Active  (Variable)  [ns=0;i=17417]
DiagnosticsLevel  (Variable)  [ns=0;i=17419]
DiagnosticsLevel  (Variable)  [ns=0;i=17410]
SubError  (Variable)  [ns=0;i=17422]
Reset  (Method)  [ns=0;i=17421]
Counters  (Object)  [ns=0;i=17423]
StatePausedByParent  (Variable)  [ns=0;i=17446]
DiagnosticsLevel  (Variable)  [ns=0;i=17449]
Active  (Variable)  [ns=0;i=17447]
Classification  (Variable)  [ns=0;i=17448]
StateOperationalFromError  (Variable)  [ns=0;i=17441]
DiagnosticsLevel  (Variable)  [ns=0;i=17444]
Classification  (Variable)  [ns=0;i=17443]
Active  (Variable)  [ns=0;i=17442]
StateDisabledByMethod  (Variable)  [ns=0;i=17451]
Active  (Variable)  [ns=0;i=17452]
Classification  (Variable)  [ns=0;i=17453]
DiagnosticsLevel  (Variable)  [ns=0;i=17454]
StateOperationalByParent  (Variable)  [ns=0;i=17436]
Active  (Variable)  [ns=0;i=17437]
DiagnosticsLevel  (Variable)  [ns=0;i=17439]
Classification  (Variable)  [ns=0;i=17438]
StateOperationalByMethod  (Variable)  [ns=0;i=17431]
DiagnosticsLevel  (Variable)  [ns=0;i=17434]
Active  (Variable)  [ns=0;i=17432]
Classification  (Variable)  [ns=0;i=17433]
StateError  (Variable)  [ns=0;i=17424]
DiagnosticsLevel  (Variable)  [ns=0;i=17429]
Classification  (Variable)  [ns=0;i=17426]
Active  (Variable)  [ns=0;i=17425]
LiveValues  (Object)  [ns=0;i=17457]
OperationalDataSetReaders  (Variable)  [ns=0;i=17464]
DiagnosticsLevel  (Variable)  [ns=0;i=17466]
ConfiguredDataSetWriters  (Variable)  [ns=0;i=17458]
DiagnosticsLevel  (Variable)  [ns=0;i=17459]
OperationalDataSetWriters  (Variable)  [ns=0;i=17462]
DiagnosticsLevel  (Variable)  [ns=0;i=17463]
ConfiguredDataSetReaders  (Variable)  [ns=0;i=17460]
DiagnosticsLevel  (Variable)  [ns=0;i=17461]
PublishedDataSets  (Object)  [ns=0;i=17371]
Status  (Object)  [ns=0;i=17405]
State  (Variable)  [ns=0;i=17406]
SecurityGroups  (Object)  [ns=0;i=15443]
AddSecurityGroup  (Method)  [ns=0;i=15444]
OutputArguments  (Variable)  [ns=0;i=15446]
InputArguments  (Variable)  [ns=0;i=15445]
RemoveSecurityGroup  (Method)  [ns=0;i=15447]
InputArguments  (Variable)  [ns=0;i=15448]
Namespaces  (Object)  [ns=0;i=11715]
   ├─ http://SUPCON.UAServer.Product  (Object)  [ns=1;i=1000]
   │  ├─ IsNamespaceSubset  (Variable)  [ns=1;i=8151043]
   │  ├─ NamespacePublicationDate  (Variable)  [ns=1;i=9170926]
   │  ├─ NamespaceUri  (Variable)  [ns=1;i=1985389]
   │  ├─ NamespaceVersion  (Variable)  [ns=1;i=2926477]
   │  ├─ StaticNodeIdTypes  (Variable)  [ns=1;i=506867]
   │  ├─ StaticNumericNodeIdRange  (Variable)  [ns=1;i=14849424]
   │  └─ StaticStringNodeIdPattern  (Variable)  [ns=1;i=14120931]
   ├─ http://opcfoundation.org/UA/DI/  (Object)  [ns=4;i=15001]
   │  ├─ DefaultAccessRestrictions  (Variable)  [ns=4;i=15033]
   │  ├─ DefaultRolePermissions  (Variable)  [ns=4;i=15031]
   │  ├─ DefaultUserRolePermissions  (Variable)  [ns=4;i=15032]
   │  ├─ IsNamespaceSubset  (Variable)  [ns=4;i=15005]
   │  ├─ NamespacePublicationDate  (Variable)  [ns=4;i=15004]
   │  ├─ NamespaceUri  (Variable)  [ns=4;i=15002]
   │  ├─ NamespaceVersion  (Variable)  [ns=4;i=15003]
   │  ├─ StaticNodeIdTypes  (Variable)  [ns=4;i=15006]
   │  ├─ StaticNumericNodeIdRange  (Variable)  [ns=4;i=15007]
   │  └─ StaticStringNodeIdPattern  (Variable)  [ns=4;i=15008]
   ├─ http://opcfoundation.org/UA/Dictionary/IRDI  (Object)  [ns=3;i=1000]
   │  ├─ IsNamespaceSubset  (Variable)  [ns=3;i=1001]
   │  ├─ NamespacePublicationDate  (Variable)  [ns=3;i=1002]
   │  ├─ NamespaceUri  (Variable)  [ns=3;i=1003]
   │  ├─ NamespaceVersion  (Variable)  [ns=3;i=1004]
   │  ├─ StaticNodeIdTypes  (Variable)  [ns=3;i=1005]
   │  ├─ StaticNumericNodeIdRange  (Variable)  [ns=3;i=1006]
   │  └─ StaticStringNodeIdPattern  (Variable)  [ns=3;i=1007]
   ├─ http://opcfoundation.org/UA/PADIM/  (Object)  [ns=5;i=1000]
   │  ├─ IsNamespaceSubset  (Variable)  [ns=5;i=1001]
   │  ├─ NamespacePublicationDate  (Variable)  [ns=5;i=1002]
   │  ├─ NamespaceUri  (Variable)  [ns=5;i=1003]
   │  ├─ NamespaceVersion  (Variable)  [ns=5;i=1004]
   │  ├─ StaticNodeIdTypes  (Variable)  [ns=5;i=1005]
   │  ├─ StaticNumericNodeIdRange  (Variable)  [ns=5;i=1006]
   │  └─ StaticStringNodeIdPattern  (Variable)  [ns=5;i=1007]
   └─ http://supcon.com/UA  (Object)  [ns=2;i=5000]
      ├─ DefaultRolePermissions  (Variable)  [ns=2;i=6007]
      ├─ IsNamespaceSubset  (Variable)  [ns=2;i=6000]
      ├─ NamespacePublicationDate  (Variable)  [ns=2;i=6001]
      ├─ NamespaceUri  (Variable)  [ns=2;i=6002]
      ├─ NamespaceVersion  (Variable)  [ns=2;i=6003]
      ├─ StaticNodeIdTypes  (Variable)  [ns=2;i=6004]
      ├─ StaticNumericNodeIdRange  (Variable)  [ns=2;i=6005]
      └─ StaticStringNodeIdPattern  (Variable)  [ns=2;i=6006]
http://opcfoundation.org/UA/  (Object)  [ns=0;i=15957]
NamespaceVersion  (Variable)  [ns=0;i=15959]
NamespacePublicationDate  (Variable)  [ns=0;i=15960]
StaticNumericNodeIdRange  (Variable)  [ns=0;i=15963]
StaticNodeIdTypes  (Variable)  [ns=0;i=15962]
DefaultUserRolePermissions  (Variable)  [ns=0;i=16135]
DefaultRolePermissions  (Variable)  [ns=0;i=16134]
IsNamespaceSubset  (Variable)  [ns=0;i=15961]
StaticStringNodeIdPattern  (Variable)  [ns=0;i=15964]
NamespaceUri  (Variable)  [ns=0;i=15958]
DefaultAccessRestrictions  (Variable)  [ns=0;i=16136]
GetMonitoredItems  (Method)  [ns=0;i=11492]
OutputArguments  (Variable)  [ns=0;i=11494]
InputArguments  (Variable)  [ns=0;i=11493]
```

## 3. 类型摘要

| NodeId | NodeClass | BrowseName | NamespaceIndex | NamespaceURI | ParentType |
|--------|-----------|------------|---------------:|-------------|------------|
| `ns=0;i=68` | VariableType | `PropertyType` | 0 | `http://opcfoundation.org/UA/` | `i=62` |
| `ns=0;i=2243` | VariableType | `SessionSecurityDiagnosticsArrayType` | 0 | `http://opcfoundation.org/UA/` | `i=63` |
| `ns=0;i=12860` | Variable | `SessionSecurityDiagnostics` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2244` | VariableType | `SessionSecurityDiagnosticsType` | 0 | `http://opcfoundation.org/UA/` | `i=63` |
| `ns=0;i=2250` | Variable | `TransportProtocol` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=63` | VariableType | `BaseDataVariableType` | 0 | `http://opcfoundation.org/UA/` | `i=62` |
| `ns=0;i=2251` | Variable | `SecurityMode` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2248` | Variable | `AuthenticationMechanism` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2252` | Variable | `SecurityPolicyUri` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2246` | Variable | `ClientUserIdOfSession` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3058` | Variable | `ClientCertificate` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2249` | Variable | `Encoding` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2245` | Variable | `SessionId` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2247` | Variable | `ClientUserIdHistory` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12864` | Variable | `AuthenticationMechanism` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12867` | Variable | `SecurityMode` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12862` | Variable | `ClientUserIdOfSession` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12868` | Variable | `SecurityPolicyUri` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12861` | Variable | `SessionId` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12869` | Variable | `ClientCertificate` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12865` | Variable | `Encoding` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12863` | Variable | `ClientUserIdHistory` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12866` | Variable | `TransportProtocol` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2020` | ObjectType | `ServerDiagnosticsType` | 0 | `http://opcfoundation.org/UA/` | `i=58` |
| `ns=0;i=2025` | Variable | `EnabledFlag` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2744` | Object | `SessionsDiagnosticsSummary` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2026` | ObjectType | `SessionsDiagnosticsSummaryType` | 0 | `http://opcfoundation.org/UA/` | `i=58` |
| `ns=0;i=12097` | Object | `<ClientName>` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2029` | ObjectType | `SessionDiagnosticsObjectType` | 0 | `http://opcfoundation.org/UA/` | `i=58` |
| `ns=0;i=2032` | Variable | `SubscriptionDiagnosticsArray` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2171` | VariableType | `SubscriptionDiagnosticsArrayType` | 0 | `http://opcfoundation.org/UA/` | `i=63` |
| `ns=0;i=12784` | Variable | `SubscriptionDiagnostics` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2172` | VariableType | `SubscriptionDiagnosticsType` | 0 | `http://opcfoundation.org/UA/` | `i=63` |
| `ns=0;i=8897` | Variable | `NextSequenceNumber` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=8902` | Variable | `EventQueueOverflowCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2175` | Variable | `Priority` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2174` | Variable | `SubscriptionId` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2998` | Variable | `EventNotificationsCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2182` | Variable | `EnableCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2184` | Variable | `RepublishRequestCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2173` | Variable | `SessionId` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2193` | Variable | `NotificationsCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=8892` | Variable | `UnacknowledgedMessageCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2191` | Variable | `DataChangeNotificationsCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2190` | Variable | `PublishRequestCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=8889` | Variable | `LatePublishRequestCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=8894` | Variable | `MonitoredItemCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=8891` | Variable | `CurrentLifetimeCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2188` | Variable | `TransferredToAltClientCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=8896` | Variable | `MonitoringQueueOverflowCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=8890` | Variable | `CurrentKeepAliveCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2187` | Variable | `TransferRequestCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2186` | Variable | `RepublishMessageCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2183` | Variable | `DisableCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2189` | Variable | `TransferredToSameClientCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2177` | Variable | `MaxKeepAliveCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=8888` | Variable | `MaxLifetimeCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2181` | Variable | `ModifyCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2176` | Variable | `PublishingInterval` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=8895` | Variable | `DisabledMonitoredItemCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=8893` | Variable | `DiscardedMessageCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2185` | Variable | `RepublishMessageRequestCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2180` | Variable | `PublishingEnabled` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2179` | Variable | `MaxNotificationsPerPublish` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12815` | Variable | `EventQueueOverflowCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12814` | Variable | `NextSequenceNumber` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12793` | Variable | `ModifyCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12792` | Variable | `PublishingEnabled` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12809` | Variable | `UnacknowledgedMessageCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12805` | Variable | `NotificationsCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12789` | Variable | `MaxKeepAliveCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12790` | Variable | `MaxLifetimeCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12788` | Variable | `PublishingInterval` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12795` | Variable | `DisableCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12786` | Variable | `SubscriptionId` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12785` | Variable | `SessionId` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12800` | Variable | `TransferredToAltClientCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12812` | Variable | `DisabledMonitoredItemCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12787` | Variable | `Priority` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12791` | Variable | `MaxNotificationsPerPublish` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12813` | Variable | `MonitoringQueueOverflowCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12807` | Variable | `CurrentKeepAliveCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12803` | Variable | `DataChangeNotificationsCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12798` | Variable | `RepublishMessageCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12802` | Variable | `PublishRequestCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12810` | Variable | `DiscardedMessageCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12806` | Variable | `LatePublishRequestCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12801` | Variable | `TransferredToSameClientCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12811` | Variable | `MonitoredItemCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12799` | Variable | `TransferRequestCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12797` | Variable | `RepublishMessageRequestCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12804` | Variable | `EventNotificationsCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12808` | Variable | `CurrentLifetimeCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12796` | Variable | `RepublishRequestCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12794` | Variable | `EnableCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2030` | Variable | `SessionDiagnostics` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2197` | VariableType | `SessionDiagnosticsVariableType` | 0 | `http://opcfoundation.org/UA/` | `i=63` |
| `ns=0;i=2218` | Variable | `HistoryReadCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2206` | Variable | `ClientLastContactTime` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2209` | Variable | `CurrentPublishRequestsInQueue` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2201` | Variable | `ServerUri` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2221` | Variable | `CallCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2219` | Variable | `WriteCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2217` | Variable | `ReadCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=11892` | Variable | `UnauthorizedRequestCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2198` | Variable | `SessionId` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2202` | Variable | `EndpointUrl` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2200` | Variable | `ClientDescription` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2208` | Variable | `CurrentMonitoredItemsCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2204` | Variable | `ActualSessionTimeout` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2220` | Variable | `HistoryUpdateCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2207` | Variable | `CurrentSubscriptionsCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2205` | Variable | `ClientConnectionTime` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2203` | Variable | `LocaleIds` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2199` | Variable | `SessionName` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=8900` | Variable | `TotalRequestCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2731` | Variable | `UnregisterNodesCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3050` | Variable | `MaxResponseMessageSize` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2730` | Variable | `RegisterNodesCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2231` | Variable | `RepublishCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2225` | Variable | `SetTriggeringCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2224` | Variable | `SetMonitoringModeCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2230` | Variable | `PublishCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2238` | Variable | `BrowseCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2229` | Variable | `SetPublishingModeCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2241` | Variable | `QueryFirstCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2235` | Variable | `AddReferencesCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2223` | Variable | `ModifyMonitoredItemsCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2222` | Variable | `CreateMonitoredItemsCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2237` | Variable | `DeleteReferencesCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2240` | Variable | `TranslateBrowsePathsToNodeIdsCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2234` | Variable | `AddNodesCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2227` | Variable | `CreateSubscriptionCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2228` | Variable | `ModifySubscriptionCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2226` | Variable | `DeleteMonitoredItemsCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2239` | Variable | `BrowseNextCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2236` | Variable | `DeleteNodesCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2233` | Variable | `DeleteSubscriptionsCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2242` | Variable | `QueryNextCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2232` | Variable | `TransferSubscriptionsCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3172` | Variable | `BrowseCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3176` | Variable | `QueryNextCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3177` | Variable | `RegisterNodesCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3160` | Variable | `DeleteMonitoredItemsCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3178` | Variable | `UnregisterNodesCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3171` | Variable | `DeleteReferencesCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3169` | Variable | `AddReferencesCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3174` | Variable | `TranslateBrowsePathsToNodeIdsCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3167` | Variable | `DeleteSubscriptionsCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3175` | Variable | `QueryFirstCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=8898` | Variable | `TotalRequestCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3168` | Variable | `AddNodesCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3166` | Variable | `TransferSubscriptionsCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3173` | Variable | `BrowseNextCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3164` | Variable | `PublishCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3165` | Variable | `RepublishCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3163` | Variable | `SetPublishingModeCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3162` | Variable | `ModifySubscriptionCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3161` | Variable | `CreateSubscriptionCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3170` | Variable | `DeleteNodesCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3159` | Variable | `SetTriggeringCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3156` | Variable | `CreateMonitoredItemsCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3152` | Variable | `HistoryReadCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3132` | Variable | `SessionName` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3158` | Variable | `SetMonitoringModeCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3135` | Variable | `EndpointUrl` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3157` | Variable | `ModifyMonitoredItemsCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3151` | Variable | `ReadCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3142` | Variable | `CurrentMonitoredItemsCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3153` | Variable | `WriteCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3134` | Variable | `ServerUri` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3138` | Variable | `MaxResponseMessageSize` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3141` | Variable | `CurrentSubscriptionsCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3139` | Variable | `ClientConnectionTime` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3137` | Variable | `ActualSessionTimeout` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3136` | Variable | `LocaleIds` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3143` | Variable | `CurrentPublishRequestsInQueue` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3140` | Variable | `ClientLastContactTime` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3131` | Variable | `SessionId` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3154` | Variable | `HistoryUpdateCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3133` | Variable | `ClientDescription` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=11891` | Variable | `UnauthorizedRequestCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3155` | Variable | `CallCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2031` | Variable | `SessionSecurityDiagnostics` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3186` | Variable | `SecurityPolicyUri` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3185` | Variable | `SecurityMode` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3180` | Variable | `ClientUserIdOfSession` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3184` | Variable | `TransportProtocol` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3183` | Variable | `Encoding` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3187` | Variable | `ClientCertificate` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3182` | Variable | `AuthenticationMechanism` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3181` | Variable | `ClientUserIdHistory` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3179` | Variable | `SessionId` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12142` | Variable | `SessionSecurityDiagnostics` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12150` | Variable | `SecurityPolicyUri` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12149` | Variable | `SecurityMode` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12148` | Variable | `TransportProtocol` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12147` | Variable | `Encoding` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12151` | Variable | `ClientCertificate` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12146` | Variable | `AuthenticationMechanism` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12145` | Variable | `ClientUserIdHistory` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12144` | Variable | `ClientUserIdOfSession` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12143` | Variable | `SessionId` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12152` | Variable | `SubscriptionDiagnosticsArray` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12098` | Variable | `SessionDiagnostics` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12107` | Variable | `ClientConnectionTime` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12131` | Variable | `AddNodesCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12108` | Variable | `ClientLastContactTime` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12124` | Variable | `CreateSubscriptionCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12129` | Variable | `TransferSubscriptionsCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12111` | Variable | `CurrentPublishRequestsInQueue` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12122` | Variable | `SetTriggeringCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12127` | Variable | `PublishCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12114` | Variable | `ReadCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12112` | Variable | `TotalRequestCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12132` | Variable | `AddReferencesCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12106` | Variable | `MaxResponseMessageSize` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12135` | Variable | `BrowseCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12130` | Variable | `DeleteSubscriptionsCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12125` | Variable | `ModifySubscriptionCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12110` | Variable | `CurrentMonitoredItemsCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12120` | Variable | `ModifyMonitoredItemsCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12105` | Variable | `ActualSessionTimeout` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12119` | Variable | `CreateMonitoredItemsCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12134` | Variable | `DeleteReferencesCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12133` | Variable | `DeleteNodesCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12117` | Variable | `HistoryUpdateCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12116` | Variable | `WriteCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12113` | Variable | `UnauthorizedRequestCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12128` | Variable | `RepublishCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12109` | Variable | `CurrentSubscriptionsCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12126` | Variable | `SetPublishingModeCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12121` | Variable | `SetMonitoringModeCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12123` | Variable | `DeleteMonitoredItemsCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12118` | Variable | `CallCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12104` | Variable | `LocaleIds` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12115` | Variable | `HistoryReadCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12100` | Variable | `SessionName` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12102` | Variable | `ServerUri` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12099` | Variable | `SessionId` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12103` | Variable | `EndpointUrl` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12101` | Variable | `ClientDescription` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12137` | Variable | `TranslateBrowsePathsToNodeIdsCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12136` | Variable | `BrowseNextCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12139` | Variable | `QueryNextCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12141` | Variable | `UnregisterNodesCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12140` | Variable | `RegisterNodesCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12138` | Variable | `QueryFirstCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2028` | Variable | `SessionSecurityDiagnosticsArray` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2027` | Variable | `SessionDiagnosticsArray` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2196` | VariableType | `SessionDiagnosticsArrayType` | 0 | `http://opcfoundation.org/UA/` | `i=63` |
| `ns=0;i=12816` | Variable | `SessionDiagnostics` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12847` | Variable | `TransferSubscriptionsCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12856` | Variable | `QueryFirstCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12855` | Variable | `TranslateBrowsePathsToNodeIdsCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12851` | Variable | `DeleteNodesCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12850` | Variable | `AddReferencesCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12849` | Variable | `AddNodesCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12858` | Variable | `RegisterNodesCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12859` | Variable | `UnregisterNodesCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12854` | Variable | `BrowseNextCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12853` | Variable | `BrowseCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12852` | Variable | `DeleteReferencesCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12848` | Variable | `DeleteSubscriptionsCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12857` | Variable | `QueryNextCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12846` | Variable | `RepublishCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12834` | Variable | `WriteCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12821` | Variable | `EndpointUrl` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12817` | Variable | `SessionId` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12825` | Variable | `ClientConnectionTime` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12838` | Variable | `ModifyMonitoredItemsCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12836` | Variable | `CallCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12835` | Variable | `HistoryUpdateCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12841` | Variable | `DeleteMonitoredItemsCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12827` | Variable | `CurrentSubscriptionsCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12839` | Variable | `SetMonitoringModeCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12823` | Variable | `ActualSessionTimeout` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12818` | Variable | `SessionName` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12842` | Variable | `CreateSubscriptionCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12840` | Variable | `SetTriggeringCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12833` | Variable | `HistoryReadCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12831` | Variable | `UnauthorizedRequestCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12843` | Variable | `ModifySubscriptionCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12829` | Variable | `CurrentPublishRequestsInQueue` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12822` | Variable | `LocaleIds` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12845` | Variable | `PublishCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12820` | Variable | `ServerUri` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12832` | Variable | `ReadCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12837` | Variable | `CreateMonitoredItemsCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12826` | Variable | `ClientLastContactTime` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12830` | Variable | `TotalRequestCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12828` | Variable | `CurrentMonitoredItemsCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12824` | Variable | `MaxResponseMessageSize` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12844` | Variable | `SetPublishingModeCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12819` | Variable | `ClientDescription` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3129` | Variable | `SessionDiagnosticsArray` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3130` | Variable | `SessionSecurityDiagnosticsArray` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2023` | Variable | `SubscriptionDiagnosticsArray` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2021` | Variable | `ServerDiagnosticsSummary` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2150` | VariableType | `ServerDiagnosticsSummaryType` | 0 | `http://opcfoundation.org/UA/` | `i=63` |
| `ns=0;i=2153` | Variable | `CumulatedSessionCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2163` | Variable | `RejectedRequestsCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2155` | Variable | `RejectedSessionCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2152` | Variable | `CurrentSessionCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2151` | Variable | `ServerViewCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2159` | Variable | `PublishingIntervalCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2162` | Variable | `SecurityRejectedRequestsCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2161` | Variable | `CumulatedSubscriptionCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2160` | Variable | `CurrentSubscriptionCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2157` | Variable | `SessionAbortCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2154` | Variable | `SecurityRejectedSessionCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2156` | Variable | `SessionTimeoutCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3117` | Variable | `CurrentSessionCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3116` | Variable | `ServerViewCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3122` | Variable | `SessionAbortCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3118` | Variable | `CumulatedSessionCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3127` | Variable | `SecurityRejectedRequestsCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3121` | Variable | `SessionTimeoutCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3125` | Variable | `CurrentSubscriptionCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3119` | Variable | `SecurityRejectedSessionCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3120` | Variable | `RejectedSessionCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3128` | Variable | `RejectedRequestsCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3126` | Variable | `CumulatedSubscriptionCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3124` | Variable | `PublishingIntervalCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2022` | Variable | `SamplingIntervalDiagnosticsArray` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2164` | VariableType | `SamplingIntervalDiagnosticsArrayType` | 0 | `http://opcfoundation.org/UA/` | `i=63` |
| `ns=0;i=12779` | Variable | `SamplingIntervalDiagnostics` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2165` | VariableType | `SamplingIntervalDiagnosticsType` | 0 | `http://opcfoundation.org/UA/` | `i=63` |
| `ns=0;i=2166` | Variable | `SamplingInterval` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=11699` | Variable | `DisabledMonitoredItemsSamplingCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=11698` | Variable | `MaxSampledMonitoredItemsCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=11697` | Variable | `SampledMonitoredItemsCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12780` | Variable | `SamplingInterval` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12783` | Variable | `DisabledMonitoredItemsSamplingCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12782` | Variable | `MaxSampledMonitoredItemsCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12781` | Variable | `SampledMonitoredItemsCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=2;i=2013` | VariableType | `DiagnosisVariableType` | 2 | `http://supcon.com/UA` | `i=2372` |
| `ns=2;i=6346` | Variable | `Description` | 2 | `http://supcon.com/UA` | `-` |
| `ns=0;i=58` | ObjectType | `BaseObjectType` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=14643` | ObjectType | `PubSubStatusType` | 0 | `http://opcfoundation.org/UA/` | `i=58` |
| `ns=0;i=14644` | Variable | `State` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2368` | VariableType | `AnalogItemType` | 0 | `http://opcfoundation.org/UA/` | `i=15318` |
| `ns=0;i=2369` | Variable | `EURange` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2330` | ObjectType | `HistoryServerCapabilitiesType` | 0 | `http://opcfoundation.org/UA/` | `i=58` |
| `ns=0;i=2338` | Variable | `DeleteAtTimeCapability` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2331` | Variable | `AccessHistoryDataCapability` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2334` | Variable | `InsertDataCapability` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=11278` | Variable | `InsertEventCapability` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2335` | Variable | `ReplaceDataCapability` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2332` | Variable | `AccessHistoryEventsCapability` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=11501` | Variable | `DeleteEventCapability` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2336` | Variable | `UpdateDataCapability` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2337` | Variable | `DeleteRawCapability` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=11280` | Variable | `UpdateEventCapability` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=11279` | Variable | `ReplaceEventCapability` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=11270` | Variable | `InsertAnnotationCapability` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=19094` | Variable | `ServerTimestampSupported` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=11268` | Variable | `MaxReturnDataValues` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=11269` | Variable | `MaxReturnEventValues` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=11172` | Object | `AggregateFunctions` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=61` | ObjectType | `FolderType` | 0 | `http://opcfoundation.org/UA/` | `i=58` |
| `ns=0;i=17598` | ObjectType | `IrdiDictionaryEntryType` | 0 | `http://opcfoundation.org/UA/` | `i=17589` |
| `ns=0;i=14416` | ObjectType | `PublishSubscribeType` | 0 | `http://opcfoundation.org/UA/` | `i=15906` |
| `ns=0;i=17479` | Variable | `SupportedTransportProfiles` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=15844` | Object | `Status` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=15845` | Variable | `State` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=18715` | Object | `Diagnostics` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=19732` | ObjectType | `PubSubDiagnosticsRootType` | 0 | `http://opcfoundation.org/UA/` | `i=19677` |
| `ns=0;i=19777` | Object | `LiveValues` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=19784` | Variable | `OperationalDataSetReaders` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=19785` | Variable | `DiagnosticsLevel` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=19782` | Variable | `OperationalDataSetWriters` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=19783` | Variable | `DiagnosticsLevel` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=19780` | Variable | `ConfiguredDataSetReaders` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=19781` | Variable | `DiagnosticsLevel` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=19778` | Variable | `ConfiguredDataSetWriters` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=19779` | Variable | `DiagnosticsLevel` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=18728` | Variable | `SubError` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=18722` | Variable | `TotalError` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=19725` | VariableType | `PubSubDiagnosticsCounterType` | 0 | `http://opcfoundation.org/UA/` | `i=63` |
| `ns=0;i=19728` | Variable | `DiagnosticsLevel` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=19729` | Variable | `TimeFirstChange` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=19727` | Variable | `Classification` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=19726` | Variable | `Active` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=18725` | Variable | `DiagnosticsLevel` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=18724` | Variable | `Classification` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=18723` | Variable | `Active` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=18729` | Object | `Counters` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=18755` | Variable | `StateDisabledByMethod` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=18758` | Variable | `DiagnosticsLevel` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=18757` | Variable | `Classification` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=18756` | Variable | `Active` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=18745` | Variable | `StateOperationalFromError` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=18746` | Variable | `Active` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=18748` | Variable | `DiagnosticsLevel` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=18747` | Variable | `Classification` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=18740` | Variable | `StateOperationalByParent` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=18742` | Variable | `Classification` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=18743` | Variable | `DiagnosticsLevel` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=18741` | Variable | `Active` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=18735` | Variable | `StateOperationalByMethod` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=18738` | Variable | `DiagnosticsLevel` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=18736` | Variable | `Active` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=18737` | Variable | `Classification` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=18730` | Variable | `StateError` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=18733` | Variable | `DiagnosticsLevel` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=18731` | Variable | `Active` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=18732` | Variable | `Classification` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=18750` | Variable | `StatePausedByParent` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=18752` | Variable | `Classification` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=18751` | Variable | `Active` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=18753` | Variable | `DiagnosticsLevel` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=18760` | Object | `LiveValues` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=18761` | Variable | `ConfiguredDataSetWriters` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=18762` | Variable | `DiagnosticsLevel` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=18767` | Variable | `OperationalDataSetReaders` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=18768` | Variable | `DiagnosticsLevel` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=18763` | Variable | `ConfiguredDataSetReaders` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=18764` | Variable | `DiagnosticsLevel` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=18765` | Variable | `OperationalDataSetWriters` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=18766` | Variable | `DiagnosticsLevel` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=18716` | Variable | `DiagnosticsLevel` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=18717` | Variable | `TotalInformation` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=18720` | Variable | `DiagnosticsLevel` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=18719` | Variable | `Classification` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=18718` | Variable | `Active` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=14434` | Object | `PublishedDataSets` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=14477` | ObjectType | `DataSetFolderType` | 0 | `http://opcfoundation.org/UA/` | `i=61` |
| `ns=0;i=14487` | Object | `<PublishedDataSetName>` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=14509` | ObjectType | `PublishedDataSetType` | 0 | `http://opcfoundation.org/UA/` | `i=58` |
| `ns=0;i=16759` | Variable | `DataSetClassId` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=15229` | Variable | `DataSetMetaData` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=14519` | Variable | `ConfigurationVersion` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=15481` | Object | `ExtensionFields` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=15489` | ObjectType | `ExtensionFieldsType` | 0 | `http://opcfoundation.org/UA/` | `i=58` |
| `ns=0;i=15490` | Variable | `<ExtensionFieldName>` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=15221` | Variable | `DataSetMetaData` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=14489` | Variable | `ConfigurationVersion` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=11564` | ObjectType | `OperationLimitsType` | 0 | `http://opcfoundation.org/UA/` | `i=61` |
| `ns=0;i=11565` | Variable | `MaxNodesPerRead` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12161` | Variable | `MaxNodesPerHistoryReadData` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=11567` | Variable | `MaxNodesPerWrite` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12162` | Variable | `MaxNodesPerHistoryReadEvents` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=11572` | Variable | `MaxNodesPerTranslateBrowsePathsToNodeIds` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12164` | Variable | `MaxNodesPerHistoryUpdateEvents` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=11574` | Variable | `MaxMonitoredItemsPerCall` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=11573` | Variable | `MaxNodesPerNodeManagement` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12163` | Variable | `MaxNodesPerHistoryUpdateData` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=11571` | Variable | `MaxNodesPerRegisterNodes` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=11570` | Variable | `MaxNodesPerBrowse` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=11569` | Variable | `MaxNodesPerMethodCall` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2034` | ObjectType | `ServerRedundancyType` | 0 | `http://opcfoundation.org/UA/` | `i=58` |
| `ns=0;i=2035` | Variable | `RedundancySupport` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2138` | VariableType | `ServerStatusType` | 0 | `http://opcfoundation.org/UA/` | `i=63` |
| `ns=0;i=2142` | Variable | `BuildInfo` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3051` | VariableType | `BuildInfoType` | 0 | `http://opcfoundation.org/UA/` | `i=63` |
| `ns=0;i=3057` | Variable | `BuildDate` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3053` | Variable | `ManufacturerName` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3056` | Variable | `BuildNumber` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3055` | Variable | `SoftwareVersion` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3052` | Variable | `ProductUri` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3054` | Variable | `ProductName` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3703` | Variable | `BuildDate` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3701` | Variable | `SoftwareVersion` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3702` | Variable | `BuildNumber` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3700` | Variable | `ProductName` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3699` | Variable | `ManufacturerName` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3698` | Variable | `ProductUri` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2752` | Variable | `SecondsTillShutdown` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2753` | Variable | `ShutdownReason` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2140` | Variable | `CurrentTime` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2139` | Variable | `StartTime` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2141` | Variable | `State` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=11616` | ObjectType | `NamespaceMetadataType` | 0 | `http://opcfoundation.org/UA/` | `i=58` |
| `ns=0;i=16137` | Variable | `DefaultRolePermissions` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=11618` | Variable | `NamespaceVersion` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=11620` | Variable | `IsNamespaceSubset` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=11621` | Variable | `StaticNodeIdTypes` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=11619` | Variable | `NamespacePublicationDate` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=16138` | Variable | `DefaultUserRolePermissions` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=11623` | Variable | `StaticStringNodeIdPattern` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=11622` | Variable | `StaticNumericNodeIdRange` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=16139` | Variable | `DefaultAccessRestrictions` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=11617` | Variable | `NamespaceUri` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=11624` | Object | `NamespaceFile` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=11595` | ObjectType | `AddressSpaceFileType` | 0 | `http://opcfoundation.org/UA/` | `i=11575` |
| `ns=0;i=12690` | Variable | `Writable` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12691` | Variable | `UserWritable` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=11628` | Variable | `OpenCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=11625` | Variable | `Size` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=11645` | ObjectType | `NamespacesType` | 0 | `http://opcfoundation.org/UA/` | `i=58` |
| `ns=0;i=11646` | Object | `<NamespaceIdentifier>` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=11651` | Variable | `StaticNodeIdTypes` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=11650` | Variable | `IsNamespaceSubset` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=11648` | Variable | `NamespaceVersion` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=11653` | Variable | `StaticStringNodeIdPattern` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=11652` | Variable | `StaticNumericNodeIdRange` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=11649` | Variable | `NamespacePublicationDate` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=11647` | Variable | `NamespaceUri` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=23456` | ObjectType | `AliasNameCategoryType` | 0 | `http://opcfoundation.org/UA/` | `i=61` |
| `ns=0;i=15452` | ObjectType | `SecurityGroupFolderType` | 0 | `http://opcfoundation.org/UA/` | `i=61` |
| `ns=0;i=15459` | Object | `<SecurityGroupName>` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=15471` | ObjectType | `SecurityGroupType` | 0 | `http://opcfoundation.org/UA/` | `i=58` |
| `ns=0;i=15472` | Variable | `SecurityGroupId` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=15056` | Variable | `MaxPastKeyCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=15046` | Variable | `KeyLifetime` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=15048` | Variable | `MaxFutureKeyCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=15047` | Variable | `SecurityPolicyUri` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=15460` | Variable | `SecurityGroupId` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=15043` | Variable | `MaxPastKeyCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=15012` | Variable | `MaxFutureKeyCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=15010` | Variable | `KeyLifetime` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=15011` | Variable | `SecurityPolicyUri` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=77` | ObjectType | `ModellingRuleType` | 0 | `http://opcfoundation.org/UA/` | `i=58` |
| `ns=0;i=111` | Variable | `NamingRule` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=2;i=1110` | ObjectType | `SolenoidValveType` | 2 | `http://supcon.com/UA` | `ns=2;i=1031` |
| `ns=2;i=1031` | ObjectType | `SIMPADeviceType` | 2 | `http://supcon.com/UA` | `ns=4;i=15063` |
| `ns=4;i=15063` | ObjectType | `ComponentType` | 4 | `http://opcfoundation.org/UA/DI/` | `ns=4;i=1001` |
| `ns=4;i=1001` | ObjectType | `TopologyElementType` | 4 | `http://opcfoundation.org/UA/DI/` | `i=58` |
| `ns=4;i=5003` | Object | `MethodSet` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=4;i=5002` | Object | `ParameterSet` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=4;i=6017` | Variable | `<ParameterIdentifier>` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=4;i=6014` | Object | `Identification` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=4;i=1005` | ObjectType | `FunctionalGroupType` | 4 | `http://opcfoundation.org/UA/DI/` | `i=61` |
| `ns=4;i=6027` | Object | `<GroupIdentifier>` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=4;i=6242` | Variable | `UIElement` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=4;i=6246` | VariableType | `UIElementType` | 4 | `http://opcfoundation.org/UA/DI/` | `i=63` |
| `ns=4;i=6243` | Variable | `UIElement` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=4;i=6161` | Object | `Lock` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=4;i=6388` | ObjectType | `LockingServicesType` | 4 | `http://opcfoundation.org/UA/DI/` | `i=58` |
| `ns=4;i=6391` | Variable | `LockingUser` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=4;i=15890` | Variable | `DefaultInstanceBrowseName` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=4;i=6534` | Variable | `Locked` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=4;i=6390` | Variable | `LockingClient` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=4;i=6392` | Variable | `RemainingLockTime` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=4;i=6165` | Variable | `RemainingLockTime` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=4;i=6163` | Variable | `LockingClient` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=4;i=6164` | Variable | `LockingUser` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=4;i=6468` | Variable | `Locked` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=4;i=6567` | Object | `<GroupIdentifier>` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=4;i=15095` | Variable | `SerialNumber` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=4;i=15088` | Variable | `Model` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=4;i=15096` | Variable | `ProductInstanceUri` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=4;i=15087` | Variable | `ManufacturerUri` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=4;i=15089` | Variable | `HardwareRevision` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=4;i=15090` | Variable | `SoftwareRevision` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=4;i=15091` | Variable | `DeviceRevision` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=4;i=15086` | Variable | `Manufacturer` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=4;i=15092` | Variable | `ProductCode` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=4;i=15094` | Variable | `DeviceClass` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=4;i=15097` | Variable | `RevisionCounter` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=4;i=15098` | Variable | `AssetId` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=4;i=15093` | Variable | `DeviceManual` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=4;i=15099` | Variable | `ComponentName` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=2;i=7232` | Variable | `Description` | 2 | `http://supcon.com/UA` | `-` |
| `ns=2;i=7229` | Variable | `ManufacturerCode` | 2 | `http://supcon.com/UA` | `-` |
| `ns=2;i=7230` | Variable | `ModelCode` | 2 | `http://supcon.com/UA` | `-` |
| `ns=2;i=6153` | Variable | `AssetId` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=2;i=7300` | Variable | `CSProjectName` | 2 | `http://supcon.com/UA` | `-` |
| `ns=2;i=5034` | Object | `ControlTagRelationSet` | 2 | `http://supcon.com/UA` | `-` |
| `ns=2;i=5046` | Object | `<TagRelationIdentifier>` | 2 | `http://supcon.com/UA` | `-` |
| `ns=2;i=1022` | ObjectType | `SignalToControlTagRelationType` | 2 | `http://supcon.com/UA` | `i=58` |
| `ns=2;i=6174` | Variable | `SignalTag` | 2 | `http://supcon.com/UA` | `-` |
| `ns=2;i=5033` | Object | `ControlTag` | 2 | `http://supcon.com/UA` | `-` |
| `ns=2;i=1035` | ObjectType | `SIMControlComponentType` | 2 | `http://supcon.com/UA` | `ns=4;i=1001` |
| `ns=2;i=7021` | Variable | `Description` | 2 | `http://supcon.com/UA` | `-` |
| `ns=2;i=5031` | Object | `Alarms` | 2 | `http://supcon.com/UA` | `-` |
| `ns=0;i=16405` | ObjectType | `AlarmGroupType` | 0 | `http://opcfoundation.org/UA/` | `i=61` |
| `ns=2;s=P_2621a4f973194b151ee2ca5ecdb94e53` | Variable | `SignalTag` | 2 | `http://supcon.com/UA` | `-` |
| `ns=2;s=P_309ba657a18f5a0ae33e98c95e9bfd32` | Object | `ControlTag` | 2 | `http://supcon.com/UA` | `-` |
| `ns=2;i=5048` | Object | `DeviceTypeImage` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=2;i=6154` | Variable | `<ImageIdentifier>` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=2;i=5049` | Object | `Documentation` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=2;i=6509` | Variable | `<DocumentIdentifier>` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=2;i=5055` | Object | `ProtocolSupport` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=2;i=6582` | Variable | `<ProtocolSupportIdentifier>` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=2;i=5068` | Object | `PADIMView` | 2 | `http://supcon.com/UA` | `-` |
| `ns=5;i=1009` | ObjectType | `PADIMType` | 5 | `http://opcfoundation.org/UA/PADIM/` | `ns=4;i=15063` |
| `ns=5;i=1010` | Variable | `Manufacturer` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=5;i=1012` | Variable | `Model` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=5;i=1011` | Variable | `ManufacturerUri` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=5;i=1014` | Variable | `SoftwareRevision` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=5;i=1015` | Variable | `HardwareRevision` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=5;i=1016` | Variable | `ProductCode` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=5;i=1013` | Variable | `SerialNumber` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=5;i=1020` | Variable | `ProductInstanceUri` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=5;i=1019` | Variable | `AssetId` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=5;i=1017` | Variable | `RevisionCounter` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=5;i=1025` | Object | `SubDevices` | 5 | `http://opcfoundation.org/UA/PADIM/` | `-` |
| `ns=4;i=1004` | ObjectType | `ConfigurableObjectType` | 4 | `http://opcfoundation.org/UA/DI/` | `i=58` |
| `ns=4;i=5004` | Object | `SupportedTypes` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=4;i=6026` | Object | `<ObjectIdentifier>` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=5;i=1026` | Object | `SupportedTypes` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=5;i=1034` | Object | `SignalSet` | 5 | `http://opcfoundation.org/UA/PADIM/` | `-` |
| `ns=5;i=1021` | ObjectType | `SignalSetType` | 5 | `http://opcfoundation.org/UA/PADIM/` | `i=58` |
| `ns=5;i=1024` | Object | `<SignalIdentifier>` | 5 | `http://opcfoundation.org/UA/PADIM/` | `-` |
| `ns=5;i=1008` | ObjectType | `SignalType` | 5 | `http://opcfoundation.org/UA/PADIM/` | `i=58` |
| `ns=5;i=1035` | Variable | `SignalTag` | 5 | `http://opcfoundation.org/UA/PADIM/` | `-` |
| `ns=5;s=P_9ed9ca2e3e51494ce245c8d837abf291` | Variable | `SignalTag` | 5 | `http://opcfoundation.org/UA/PADIM/` | `-` |
| `ns=5;i=1018` | Object | `DeviceHealthAlarms` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=5;i=1032` | Variable | `DateOfLastChange` | 5 | `http://opcfoundation.org/UA/PADIM/` | `-` |
| `ns=5;i=1033` | Variable | `DisplayLanguage` | 5 | `http://opcfoundation.org/UA/PADIM/` | `-` |
| `ns=5;i=1029` | Variable | `DeviceHealth` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=4;s=P_b18a709babf2d368f93b6fe31dcc38e0` | Variable | `SerialNumber` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=4;s=P_8dae134830438f61674ca19fa75b95c0` | Variable | `HardwareRevision` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=4;s=P_c7da688418d22567299566714002a7ff` | Variable | `Manufacturer` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=4;s=P_f1d7dbeb49c7a5c77656972a6d4f8dbc` | Variable | `Model` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=4;s=P_b2cf12b14bdbbd7081309b2f7f4cee4a` | Variable | `ProductInstanceUri` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=4;s=P_458e45c6d8cf64251fe526cab8b7e7c5` | Variable | `ManufacturerUri` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=4;s=P_3ff34046038bcbdbbb87a8ef5a981e38` | Variable | `ProductCode` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=4;s=P_5faa828061b640c915c1c7678d84f3d5` | Variable | `RevisionCounter` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=4;s=P_4f53c0b446dfb639c913e37df714a0e2` | Variable | `AssetId` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=4;s=P_fecc107a2dfb803c3d7f509e16d466e8` | Variable | `SoftwareRevision` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=4;s=P_ec7d7a4dfecd8318e0b3427d216c9b1e` | Variable | `DeviceHealth` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=2;i=5051` | Object | `ImageSet` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=2;i=6581` | Variable | `<ImageIdentifier>` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=2;i=5056` | Object | `Protocol` | 2 | `http://supcon.com/UA` | `-` |
| `ns=4;i=1006` | ObjectType | `ProtocolType` | 4 | `http://opcfoundation.org/UA/DI/` | `i=58` |
| `ns=2;i=5074` | Object | `OperationCounters` | 2 | `http://supcon.com/UA` | `-` |
| `ns=2;i=6583` | Variable | `DateOfLastOnline` | 2 | `http://supcon.com/UA` | `-` |
| `ns=2;i=6584` | Variable | `WorkingDays` | 2 | `http://supcon.com/UA` | `-` |
| `ns=2;i=5113` | Object | `MethodSet` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=2;i=5086` | Object | `Runtime` | 2 | `http://supcon.com/UA` | `-` |
| `ns=2;i=7231` | Variable | `AlarmStatusCode` | 2 | `http://supcon.com/UA` | `-` |
| `ns=2;i=6685` | Variable | `OnlineState` | 2 | `http://supcon.com/UA` | `-` |
| `ns=0;i=2373` | VariableType | `TwoStateDiscreteType` | 0 | `http://opcfoundation.org/UA/` | `i=2372` |
| `ns=0;i=2375` | Variable | `TrueState` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2374` | Variable | `FalseState` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;s=P_260b95756dbd52b088b881090cff3b48` | Variable | `TrueState` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;s=P_b3689b80613c8c9c4d6b6c45a749fe54` | Variable | `FalseState` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=2;i=5114` | Object | `ParameterSet` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=2;i=6686` | Variable | `<ParameterIdentifier>` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=2;i=7239` | Variable | `SerialNumber` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=2;i=7236` | Variable | `Manufacturer` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=2;i=7234` | Variable | `DeviceClass` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=2;i=7233` | Variable | `Description` | 2 | `http://supcon.com/UA` | `-` |
| `ns=2;i=7238` | Variable | `Model` | 4 | `http://opcfoundation.org/UA/DI/` | `-` |
| `ns=2;i=5209` | Object | `Configuration` | 2 | `http://supcon.com/UA` | `-` |
| `ns=2;i=7246` | Variable | `SnapshotPeriod` | 2 | `http://supcon.com/UA` | `-` |
| `ns=2;i=7303` | Variable | `CurrentType` | 2 | `http://supcon.com/UA` | `-` |
| `ns=2;i=5208` | Object | `Runtime` | 2 | `http://supcon.com/UA` | `-` |
| `ns=2;i=7243` | Variable | `FaultState` | 2 | `http://supcon.com/UA` | `-` |
| `ns=2;i=7244` | Variable | `TypeMismatch` | 2 | `http://supcon.com/UA` | `-` |
| `ns=2;i=7240` | Variable | `OnlineState` | 2 | `http://supcon.com/UA` | `-` |
| `ns=0;s=P_f871e5ce6f5ce9c6520b63dadc8d1716` | Variable | `FalseState` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;s=P_44d54af0b73114e3edf5783cdb814922` | Variable | `TrueState` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=2;i=7241` | Variable | `Current` | 2 | `http://supcon.com/UA` | `-` |
| `ns=0;s=P_128ff631c27ffca909b305443d6d6564` | Variable | `EURange` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=2;i=7242` | Variable | `ActionSnapshot` | 2 | `http://supcon.com/UA` | `-` |
| `ns=0;i=2013` | ObjectType | `ServerCapabilitiesType` | 0 | `http://opcfoundation.org/UA/` | `i=58` |
| `ns=0;i=2734` | Variable | `MaxHistoryContinuationPoints` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2732` | Variable | `MaxBrowseContinuationPoints` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2733` | Variable | `MaxQueryContinuationPoints` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2017` | Variable | `MinSupportedSampleRate` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2016` | Variable | `LocaleIdArray` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3049` | Variable | `SoftwareCertificates` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2014` | Variable | `ServerProfileArray` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=11550` | Variable | `MaxStringLength` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=11549` | Variable | `MaxArrayLength` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12910` | Variable | `MaxByteStringLength` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2754` | Object | `AggregateFunctions` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=11551` | Object | `OperationLimits` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2019` | Object | `ModellingRules` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=16295` | Object | `RoleSet` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=15607` | ObjectType | `RoleSetType` | 0 | `http://opcfoundation.org/UA/` | `i=58` |
| `ns=0;i=15608` | Object | `<RoleName>` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=15620` | ObjectType | `RoleType` | 0 | `http://opcfoundation.org/UA/` | `i=58` |
| `ns=0;i=16174` | Variable | `Applications` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=16175` | Variable | `Endpoints` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=16173` | Variable | `Identities` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=15411` | Variable | `EndpointsExclude` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=15410` | Variable | `ApplicationsExclude` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=16162` | Variable | `Identities` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=11562` | Variable | `<VendorCapability>` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2137` | VariableType | `ServerVendorCapabilityType` | 0 | `http://opcfoundation.org/UA/` | `i=63` |
| `ns=0;i=2033` | ObjectType | `VendorServerInfoType` | 0 | `http://opcfoundation.org/UA/` | `i=58` |
| `ns=0;i=2133` | ObjectType | `GeneralModelChangeEventType` | 0 | `http://opcfoundation.org/UA/` | `i=2132` |
| `ns=0;i=2134` | Variable | `Changes` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2004` | ObjectType | `ServerType` | 0 | `http://opcfoundation.org/UA/` | `i=58` |
| `ns=0;i=2008` | Variable | `ServiceLevel` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2005` | Variable | `ServerArray` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=12882` | Variable | `EstimatedReturnTime` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2006` | Variable | `NamespaceArray` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=17612` | Variable | `LocalTime` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=15003` | Variable | `UrisVersion` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2742` | Variable | `Auditing` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2007` | Variable | `ServerStatus` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3074` | Variable | `StartTime` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3077` | Variable | `BuildInfo` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3079` | Variable | `ManufacturerName` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3082` | Variable | `BuildNumber` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3083` | Variable | `BuildDate` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3078` | Variable | `ProductUri` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3081` | Variable | `SoftwareVersion` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3080` | Variable | `ProductName` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3076` | Variable | `State` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3085` | Variable | `ShutdownReason` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3084` | Variable | `SecondsTillShutdown` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3075` | Variable | `CurrentTime` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=11527` | Object | `Namespaces` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2009` | Object | `ServerCapabilities` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3092` | Variable | `SoftwareCertificates` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3089` | Variable | `MaxBrowseContinuationPoints` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3090` | Variable | `MaxQueryContinuationPoints` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3088` | Variable | `MinSupportedSampleRate` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3087` | Variable | `LocaleIdArray` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3086` | Variable | `ServerProfileArray` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3091` | Variable | `MaxHistoryContinuationPoints` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3094` | Object | `AggregateFunctions` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3093` | Object | `ModellingRules` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2011` | Object | `VendorServerInfo` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2012` | Object | `ServerRedundancy` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3115` | Variable | `RedundancySupport` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=2010` | Object | `ServerDiagnostics` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3114` | Variable | `EnabledFlag` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3110` | Variable | `SubscriptionDiagnosticsArray` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3095` | Variable | `ServerDiagnosticsSummary` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3096` | Variable | `ServerViewCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3105` | Variable | `CurrentSubscriptionCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3106` | Variable | `CumulatedSubscriptionCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3102` | Variable | `SessionAbortCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3101` | Variable | `SessionTimeoutCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3108` | Variable | `RejectedRequestsCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3100` | Variable | `RejectedSessionCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3107` | Variable | `SecurityRejectedRequestsCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3099` | Variable | `SecurityRejectedSessionCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3104` | Variable | `PublishingIntervalCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3098` | Variable | `CumulatedSessionCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3097` | Variable | `CurrentSessionCount` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3111` | Object | `SessionsDiagnosticsSummary` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3113` | Variable | `SessionSecurityDiagnosticsArray` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=3112` | Variable | `SessionDiagnosticsArray` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=17591` | ObjectType | `DictionaryFolderType` | 0 | `http://opcfoundation.org/UA/` | `i=61` |
| `ns=0;i=17592` | Object | `<DictionaryFolderName>` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=17593` | Object | `<DictionaryEntryName>` | 0 | `http://opcfoundation.org/UA/` | `-` |
| `ns=0;i=17589` | ObjectType | `DictionaryEntryType` | 0 | `http://opcfoundation.org/UA/` | `i=58` |
| `ns=0;i=17590` | Object | `<DictionaryEntryName>` | 0 | `http://opcfoundation.org/UA/` | `-` |

## 4. 引用摘要

| ReferenceType | 数量 |
|---------------|----:|
| HasTypeDefinition | 5734 |
| HasModellingRule | 5158 |
| HasComponent | 1408 |
| HasProperty | 788 |
| HasSubtype | 228 |
| HasDictionaryEntry | 75 |
| Organizes | 37 |
| HasInterface | 35 |
| AlarmGroupMember | 1 |
| DataSetToWriter | 1 |
| GeneratesEvent | 1 |
| HasPubSubConnection | 1 |

## 5. 异常和缺失

_无错误_

## 6. 验收检查

- 自定义类型 `ns=2;i=1110`: **OK**
- 自定义类型 `ns=2;i=2013`: **OK**
- 自定义类型 `ns=4;i=1005`: **OK**
- 设备 `SOV1`: **OK**
- 设备 `SOV2`: **OK**
- 设备 `SOV3`: **OK**
- 设备 `SOV4`: **OK**
- 设备 `SOV5`: **OK**
- 设备 `SOV6`: **OK**
- 设备 `SOV7`: **OK**
- 设备 `SOV8`: **OK**
