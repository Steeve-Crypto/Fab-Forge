import asyncio
import logging
from asyncua import ua, Server, uamethod

class FabOpcUaServer:
    def __init__(self):
        self.server = Server()
        self.server.set_endpoint("opc.tcp://0.0.0.0:4840/fabforge/server/")
        self.server.set_server_name("FabForge OPC-UA Server for Terafab")
        self.server.set_security_policy([ua.SecurityPolicyType.NoSecurity])

        # Setup namespace
        self.idx = self.server.register_namespace("FabForge")
        
        # Add equipment objects (digital twin nodes)
        objects = self.server.nodes.objects
        self.equipment_folder = objects.add_folder(self.idx, "Equipment")
        
        # Lithography Tool
        self.litho = self.equipment_folder.add_object(self.idx, "LithographyTool")
        self.litho_temp = self.litho.add_variable(self.idx, "Temperature", 195.0)
        self.litho_temp.set_writ able(True)
        self.litho_status = self.litho.add_variable(self.idx, "Status", "Idle")
        
        # Etch Tool
        self.etch = self.equipment_folder.add_object(self.idx, "EtchTool")
        self.etch_pressure = self.etch.add_variable(self.idx, "Pressure", 0.01)
        self.etch_pressure.set_writable(True)
        self.etch_status = self.etch.add_variable(self.idx, "Status", "Running")
        
        # Add method for wafer processing
        @uamethod
        def process_wafer(parent, wafer_id):
            logging.info(f"Processing wafer {wafer_id} via OPC-UA")
            return f"Wafer {wafer_id} processed successfully"
        
        self.litho.add_method(self.idx, "ProcessWafer", process_wafer, [ua.VariantType.Int32], [ua.VariantType.String])
        
        logging.info("OPC-UA Server nodes configured for Terafab fab simulation")

    async def start(self):
        await self.server.start()
        logging.info("FabForge OPC-UA Server running on opc.tcp://0.0.0.0:4840")

async def main():
    logging.basicConfig(level=logging.INFO)
    server = FabOpcUaServer()
    try:
        await server.start()
    except asyncio.CancelledError:
        await server.server.stop()
        logging.info("OPC-UA Server stopped gracefully")

if __name__ == "__main__":
    asyncio.run(main())
