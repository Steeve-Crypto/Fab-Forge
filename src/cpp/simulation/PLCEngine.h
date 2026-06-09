#pragma once
#include "EquipmentStateMachine.h"
#include <vector>

class PLCEngine {
public:
    PLCEngine();
    void executeLadderLogic();  // Emulated IEC 61131-3 style
    void executeRung();         // compatibility alias for bindings
    void addEquipment(EquipmentStateMachine* eq);
    void sequenceProcess(int waferId);

private:
    std::vector<EquipmentStateMachine*> equipments_;
};
