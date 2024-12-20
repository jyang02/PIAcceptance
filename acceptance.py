import numpy as np
import ROOT

fout = ROOT.TFile.Open("pienu_rec_hst.root","RECREATE")

hNumHitsReached = ROOT.TH1F("hNumHitsReached","Primary e+ reached the tracker;Num Tracker Hits;",20,-0.5,19.5)
hNumHitsMissed = ROOT.TH1F("hNumHitsMissed","Primary e+ did not the tracker;Num Tracker Hits;",20,-0.5,19.5)

hThetaMomTotal = ROOT.TH2F("hThetaMomTotal","Primary e+ reached the tracker;cos(theta);Momentum (MeV)",25,-1,1,25,0,80)
hThetaMomReached = ROOT.TH2F("hThetaMomReached","Primary e+ reached the tracker;cos(theta);Momentum (MeV)",25,-1,1,25,0,80)
hThetaMomMissed = ROOT.TH2F("hThetaMomMissed","Primary e+ did not the tracker;cos(theta);Momentum (MeV)",25,-1,1,25,0,80)
hThetaMomAnnihil = ROOT.TH2F("hThetaMomAnnihil","Primary e+ annihilated;cos(theta);Momentum (MeV)",25,-1,1,25,0,80)

f = ROOT.TFile("sim/pienu_rec.root")
rec = f.Get("rec")

hasPrimary = 0
hasNone = 0
totEntries = 0
for ievt,evt in enumerate(rec):
    if ievt % 10000 == 0:
        print(f"{ievt} / {rec.GetEntries()}")
    if ievt == 380000:
        break

    primaryTIDs = []
    for t in evt.tagVec:
        if t.GetPDGID() == -11:
            primaryTIDs.append(t.GetTrackID())

    for s in evt.summaryVec:
        if len(s.GetPatternIndex()) != 1:
            continue        
        for pid in s.GetPatternIndex():
            p = evt.patternVec[pid]
            pos = p.GetInitStopPosition()
            if p.GetInitPID() != 211 or abs(pos.X()) > 8 or abs(pos.Y()) > 8 or pos.Z() > 4.8 or pos.Z() < 1.2:
                continue

            totEntries += 1
            TIDs = []
            for hit in s.GetTracker():
                if hit.GetTID() not in TIDs:
                    TIDs.append(hit.GetTID())
            if TIDs == []:
                hasNone += 1
                continue

            mom = s.GetPositronMomentum()
            hThetaMomTotal.Fill(np.cos(mom.Theta()),np.sqrt(mom.Mag2()))
            if any([(tid in primaryTIDs) for tid in TIDs]):
                hasPrimary += 1
                hNumHitsReached.Fill(len(s.GetTracker()))
                hThetaMomReached.Fill(np.cos(mom.Theta()),np.sqrt(mom.Mag2()))
            else:
                hNumHitsMissed.Fill(len(s.GetTracker()))
                hThetaMomMissed.Fill(np.cos(mom.Theta()),np.sqrt(mom.Mag2()))

                if (s.GetEventType() & ROOT.PIEventType.kAnhl) == ROOT.PIEventType.kAnhl:
                    hThetaMomAnnihil.Fill(np.cos(mom.Theta()),np.sqrt(mom.Mag2()))

print(f'Primary positron reached tracker in {hasPrimary/totEntries*100:.2f}% of events')
print(f'{hasNone/totEntries*100:.2f}% of events had no tracker hit')

fout.Write()
fout.Close()
f.Close()