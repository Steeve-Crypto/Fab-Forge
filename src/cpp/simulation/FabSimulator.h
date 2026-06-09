#pragma once
#include "Wafer.h"
#include "PLCEngine.h"
#include "EquipmentStateMachine.h"
#include <queue>
#include <memory>
#include <chrono>

class FabSimulator {
public:
    FabSimulator();
    void runSimulation(int numWafers, int steps);
    void addEquipment(const std::string& name);

private:
    std::vector<std::unique_ptr<Wafer>> wafers_;
    std::vector<std::string> equipment_;
    // Event queue for discrete event sim
    std::priority_queue<double> eventQueue_;
    
    // New: PLC and State Machines for IEC 61131-3 emulation and SECS/GEM basics
    // (SECS/GEM simulated via message passing in controls layer)
    std::unique_ptr<PLCEngine> plc_;
    std::unique_ptr<EquipmentStateMachine> lithoSM_;
    std::unique_ptr<EquipmentStateMachine> etchSM_;
    std::unique_ptr<EquipmentStateMachine> depoSM_;
};
