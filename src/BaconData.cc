#ifndef BaconData_cc
#define BaconData_cc

#include "DAZSLE/ZPrimePlusJet/interface/BaconData.h"

BaconData::BaconData(TTree *tree) : BaconTree(tree) {
}

BaconData::~BaconData() {
}

Int_t BaconData::GetEntry(Long64_t entry) {
	// Clear previous event

	// Load new event
	Int_t ret = fChain->GetEntry(entry);
	return ret;
}


#endif