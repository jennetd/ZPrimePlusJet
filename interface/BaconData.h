#ifndef BaconData_h
#define BaconData_h

#include <typeinfo>
#include "DAZSLE/ZPrimePlusJet/interface/BaconTree.h"
#include "TMath.h"
 /**
  * @brief      Class for exposing data from bacon ntuples.
  */
 

class BaconData : public BaconTree {
public:

	BaconData(TTree *tree=0);

	~BaconData();

	Int_t GetEntry(Long64_t entry);

	// Helper functions for exposing data without having to know branch names...
	inline Double_t AK8Puppijet0_tau21DDT() const {
		return AK8Puppijet0_tau21 + 0.063*TMath::Log(AK8Puppijet0_msd*AK8Puppijet0_msd/AK8Puppijet0_pt);
	}

	inline Double_t CA15Puppijet0_tau21DDT() const {
		return CA15Puppijet0_tau21 + 0.063*TMath::Log(CA15Puppijet0_msd*CA15Puppijet0_msd/CA15Puppijet0_pt);
	}
private:

};


#endif