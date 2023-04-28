import json

import numpy as np

fn = "commercial-4.02.cycling.json"
with open(fn) as infile:
    jsdata = json.load(infile)

# load timestamps, voltages, currents, cycle numbers
uts = []
Ewe = []
I = []
cn = []
for ts in jsdata["steps"][0]["data"]:
    uts.append(ts["uts"])
    Ewe.append(ts["raw"]["Ewe"]["n"])
    I.append(ts["raw"]["I"]["n"])
    cn.append(ts["raw"]["cycle number"])
t0 = uts[0]

# convert to numpy arrays
t = np.array(uts) - t0
Ewe = np.array(Ewe)
I = np.array(I)
cn = np.array(cn)

# find indices of sign changes in Iadd index of last point
idx = np.where(np.diff(np.sign(I)) != 0)[0]
idx = np.append(idx, len(t) - 1)

Qc = []
Qd = []
Qi = []
# integrate and store charge and discharge currents, store cycle indices
for ii, ie in enumerate(idx[1:]):
    i0 = idx[ii]
    q = np.trapz(I[i0:ie], t[i0:ie])
    if q > 0:
        Qc.append(q)
    else:
        Qd.append(abs(q))
        Qi.append(cn[ie] + 1)

import matplotlib.pyplot as plt

# plot Ewe vs time in h
fig, ax = plt.subplots()
ax.plot([i / 3600 for i in t], Ewe, marker="", ls="-", color="C0")
ax.set_xlabel("t [h]")
ax.set_ylabel("Ewe [V]")
plt.savefig("Ewe_vs_t.png")

# plot Ewe vs time in h
fig, ax = plt.subplots()
ax.plot([i / 3600 for i in t], I, marker="", ls="-", color="C1")
ax.set_xlabel("t [h]")
ax.set_ylabel("I [A]")
plt.savefig("I_vs_t.png")

# plot Qd vs cycle in mAh
fig, ax = plt.subplots()
ax.plot(Qi, [j / 3.6 for j in Qc],
        marker="o",
        ls="",
        color="C2",
        label="Q in charge")
ax.plot(Qi, [j / 3.6 for j in Qd],
        marker="o",
        ls="",
        color="C3",
        label="Q in discharge")
ax.set_xlabel("cycle number")
ax.set_ylabel("Q [mAh]")
ax.legend()
plt.savefig("Q_vs_cn.png")
