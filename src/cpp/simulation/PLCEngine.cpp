#include "PLCEngine.h"
#include <iostream>

PLCEngine::PLCEngine() {}

void PLCEngine::addEquipment(EquipmentStateMachine* eq) {
    equipments_.push_back(eq);
}

void PLCEngine::executeLadderLogic() {
    std::cout << "Executing emulated IEC 61131-3 Ladder Logic..." << std::endl;
    // Simulate rung checks for safety interlocks, sequencing
    for (auto* eq : equipments_) {
        if (eq->getCurrentState() == EquipmentState::FAULT) {
            std::cout << "EMERGENCY STOP triggered!" << std::endl;
        }
    }
}

void PLCEngine::sequenceProcess(int waferId) {
    std::cout << "PLC Sequencing wafer " << waferId << " through tools..." << std::endl;
    for (auto* eq : equipments_) {
        eq->processWafer(waferId);
    }
}
