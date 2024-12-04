import pyvisa
import logging


# Configure the logging settings
logging.basicConfig(
    level=logging.INFO,  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s'  # Format of log messages
)

rm = pyvisa.ResourceManager()
cmw = rm.open_resource("TCPIP::192.10.11.203::INSTR")
print(cmw.query("*IDN?"))
cmw.write("*RST;*OPC;*CLS")
logging.info("Logging L.15: RST, OPC and CLS fired")
print("Identity:", cmw.query("*IDN?"))  # Verify device is responsive
print("Errors:", cmw.query("SYST:ERR?"))  # Ensure no errors occurred

#RF Signal Generator:-
cmw.write("SOURce:LTE:SIGN:CELL:STATe ON;*OPC")
logging.info("Logging L.21: Activating DL LTE channel")
try:
    if(cmw.query("SOURce:LTE:SIGN:CELL:STATe:ALL?")):
        # configure frequency Band below
        print("DL LTE channel enabled, STATUS:",cmw.query("SOURce:LTE:SIGN:CELL:STATe:ALL?"))
        cmw.write("CONFigure:LTE:SIGN:PCC:BAND OB5") #Band5 configured
        logging.info("Logging L.27: Band5 Configured")
        cmw.timeout = 30000  # Increase timeout to 30 seconds

        #check supported BW "Some issue Here"
        #supported_bandwidths = cmw.query("CONFigure:LTE:SIGN:CELL:BANDwidth:PCC:DL:ALL?")
        #print("Supported DL Bandwidths for PCC:", supported_bandwidths)
        #cmw.timeout = 30000  # Increase timeout to 30 seconds

        #configure BW below "Some issue Here"
        #cmw.write("CONFigure:LTE:SIGN:CELL:BANDwidth:PCC:DL B5.0")
        #cmw.timeout = 10000  # Increase timeout to 10 seconds
        #error_response = cmw.query("SYST:ERR?")
        #logging.info(f"L31Error after setting DL bandwidth: {error_response}")
        #logging.info(f'Logging L.28: BW selected to : {cmw.query("CONFigure:LTE:SIGN:CELL:BANDwidth:PCC:DL?")}Mhz')
        #cmw.write("CONFigure:LTE:SIGN:RFSettings:PCC:CHANnel:DL 2400") #DL configured
        #logging.info("Logging: DL:2400MHz set") ###

        cmw.write("CONFigure:LTE:SIGN:DL:PCC:RSEPre:LEVel -80")   # Set RS EPRE and signal/channel power levels
        logging.info("Logging L.33:Power Level Set to -80 dBm")
        cmw.timeout = 30000  # Increase timeout to 30 seconds

        cmw.timeout = 10000  # Increase timeout to 10 seconds
        #query Ipv4 and IPV6 address
        UE_IPV4=cmw.query('SENSe:LTE:SIGN:UESinfo:UEADdress:IPV4?')
        UE_IPV6=cmw.query('SENSe:LTE:SIGN:UESinfo:UEADdress:IPV6?')
        print(f'IPV4 address is :{UE_IPV4} & IPV6 address is:{UE_IPV6}')
        print("IPV4&IPV6 Errors:", cmw.query("SYST:ERR?"))  # Ensure no errors occurred
        cmw.timeout = 10000  # Increase timeout to 10 seconds

        #query UE IMEI and IMSI Nuymber
        UE_IMEI=cmw.query('SENSe:LTE:SIGN1:UESinfo:IMEI?')
        UE_IMSI=cmw.query('SENSe:LTE:SIGN1:UESinfo:IMSI?')
        print("IMEI&IMSI Errors:", cmw.query("SYST:ERR?"))  # Ensure no errors occurred
        print(f"NIC of IMEI : {UE_IMEI} & SIM of IMSI : {UE_IMSI}")
        cmw.timeout=10000     # 10 second timeout

        # Query total DL power
        full_cell_power = cmw.query("SENSe:LTE:SIGN:DL:PCC:FCPower?")
        logging.info(f"Raw Full Cell DL Power: {full_cell_power}")
        # Reformat the power for readability
        try:
            full_cell_power_float = float(full_cell_power)
            formatted_power = f"{full_cell_power_float:.2f} dBm"
            print(" L43. Full Cell DL Power (Formatted):", formatted_power)
            logging.info(f" L44. Formatted Full Cell DL Power: {formatted_power}")
        except ValueError as e:
            print("Error converting DL Power:", e)
            logging.error(f" L47. Error formatting DL Power: {e}")

        cmw.timeout = 10000  # Increase timeout to 30 seconds

        #Query total downlink throughput
        full_DL_throughput= cmw.query("SENSe:LTE:SIGN1:CONNection:ETHRoughput:DL:ALL?")
        print(f"DL throughput is: { full_DL_throughput}")
        cmw.timeout = 10000  # Increase timeout to 30 seconds

        #Query total uplink ethernet throughput
        full_ULethernet_throughput = cmw.query("SENSe:LTE:SIGN1:CONNection:ETHRoughput:UL:ALL?")
        print(f"UL throughput is: {full_ULethernet_throughput}")

        try:
            full_DL_throughput_float = float(full_DL_throughput)
            full_UL_throughput_float = float(full_ULethernet_throughput)
            formatted_Dl_throughput = f"{full_DL_throughput_float:.2f} dBm"
            formatted_UL_throughput = f"{full_UL_throughput_float:.2f} dBm"
            print(" L77. Full Cell DL throughput (Formatted):", formatted_Dl_throughput)
            print(" L78. Full Cell Ul throughput (Formatted):", formatted_UL_throughput)

            #logging.info(f" L44. Formatted Full Cell DL Power: {formatted_Dl_throughput}")
        except ValueError as e:
            print("Error converting DL and UL throughput:", e)
            logging.error(f" L47. Error formatting DL & UL throughput: {e}")

        print("Errors:", cmw.query("SYST:ERR?"))  # Ensure no errors occurred
        cmw.timeout = 10000  # Increase timeout to 10 seconds

        #querying the UE Information
        UE_uses=cmw.query('SENSe:LTE:SIGN:UESinfo:UEUSage?')
        UE_VDDref=cmw.query('SENSe:LTE:SIGN:UESinfo:VDPReference?')
        UE_Bearer=cmw.query('SENSe:LTE:SIGN:UESinfo:UEADdress:DEDBearer:SEParate?')
        print(f'UE_uses: {UE_uses}, UE_vddref: {UE_VDDref}, UE_Bearer: {UE_Bearer}')
        cmw.timeout=1000

        #UE Report enable settings 1.Reporting Interval
        cmw.write("CONFigure:LTE:SIGN:UEReport:RINTerval I640")  # Example: 640 ms
        print("RINTerval Errors:", cmw.query("SYST:ERR?"))  # Ensure no errors occurred
        cmw.timeout = 10000  # Increase timeout to 10 seconds

        #Measurement Gap Enable (Optional)
        cmw.write("CONFigure:LTE:SIGN:UEReport:MGENable ON")
        print("MGENable Errors:", cmw.query("SYST:ERR?"))  # Ensure no errors occurred
        cmw.timeout = 10000  # Increase timeout to 10 seconds

        #Measurement Gap Period (Optional)
        cmw.write("CONFigure:LTE:SIGN:UEReport:MGPeriod G040")
        print("MGPeriod Errors:", cmw.query("SYST:ERR?"))  # Ensure no errors occurred
        cmw.timeout = 10000  # Increase timeout to 10 seconds

        #Miscalleneous settings
        cmw.write('CONFigure:LTE:SIGN:UEReport:FCOefficient:RSRP FC4')
        print("FCOefficient RSRP Errors:", cmw.query("SYST:ERR?"))  # Ensure no errors occurred
        cmw.write('CONFigure:LTE:SIGN:UEReport:FCOefficient:RSRQ FC4')
        print("FCOefficient RSRQ Errors:", cmw.query("SYST:ERR?"))  # Ensure no errors occurred
        cmw.write('CONFigure:LTE:SIGN:UEReport:WMQuantity ECNO')
        print("WMQuantity Errors:", cmw.query("SYST:ERR?"))  # Ensure no errors occurred
        cmw.write('CONFigure:LTE:SIGN:UEReport:MCSCell SF640')
        print("MCSCell Errors:", cmw.query("SYST:ERR?"))  # Ensure no errors occurred
        cmw.write('CONFigure:LTE:SIGN:UEReport:AINTerrupt OFF')
        print("AINTerrupt Errors:", cmw.query("SYST:ERR?"))  # Ensure no errors occurred
        cmw.write('CONFigure:LTE:SIGN:UEReport:ENABle ON')
        print("UEReport Enable Errors:", cmw.query("SYST:ERR?"))  # Ensure no errors occurred
        cmw.timeout = 10000  # Increase timeout to 10 seconds

        #Query the RSRP and RSRQ for PCC
        RSRP_RCOM1=cmw.query("SENSe:LTE:SIGN1:UEReport[:PCC]:RSRP?")
        print("RSRPRead Enable Errors:", cmw.query("SYST:ERR?"))  # Ensure no errors occurred
        RSRQ_RCOM1=cmw.query("SENSe:LTE:SIGN1:UEReport[:PCC]:RSRQ?")
        print("RSRQRead Enable Errors:", cmw.query("SYST:ERR?"))  # Ensure no errors occurred
        print(f"RSRP as: {RSRP_RCOM1}, RSRQ as: {RSRQ_RCOM1}")
        cmw.timeout = 10000  # Increase timeout to 10 seconds

        #Query the Modulation and coding scheme
        Mod_Cod_scheme=cmw.query("SENSe:LTE:SIGN1:CONNection:PCC:FCPRi:DL:MCSTable:DETermined?")
        print(f'Modulation and Coding scheme as: {Mod_Cod_scheme}')

        #query the RRC connection
        RRC_value=cmw.query("SENSe:LTE:SIGN1:RRCState?")
        print(f'RRC connection state as: {RRC_value}')

        #Query total DL power
        full_DL_Power=cmw.query("SENSe:LTE:SIGN1:DL[:PCC]:FCPower?")
        print(f"Total DL power is: {full_DL_Power} ")

        #turing off the LTE signal generator
        cmw.write("SOURce:LTE:SIGN1:CELL:STATe ON")


        cmw.timeout = 30000  # Increase timeout to 30 seconds

        #checking the status of LTE signal
        print(f'LTE signal generator status is: {cmw.query("SOURce:LTE:SIGN1:CELL:STATe:ALL?")}')

except pyvisa.errors.VisaIOError as e:
    print("VISA Communication Error:", str(e))
finally:
    # Close the connection
    cmw.close()

    #print("Configuration Completed:", cmw.query("*OPC?"))
    #cmw.write("INIT:LTE:SIGN:MEAS")  #Start the measurement
#print(cmw.query("FETCh:LTE:SIGN:PSWitched:STATe?"))
#cmw.write("ROUT:RF:PORT:IN RF1C, RF1")  #Configure RF1C as the input port
#cmw.write("ROUT:LTE:SIGN:SCENario:BASE")
#cmw.write("ROUT:LTE:SIGN:RF:PORT RF1C")
#print(cmw.query("SYST:HELP?"))

#print("Routing State:", cmw.query("ROUT:LTE:SIGN:SCEN:STATe?"))  #Check RF Routing


