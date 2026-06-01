# Example Independent Claim

A method for establishing a shared context identifier among a plurality of uncoordinated electronic devices, the method comprising:
(a) capturing ambient audio on each device for a predetermined duration;
(b) extracting a spectral fingerprint from said ambient audio;
(c) generating a hash chain from said spectral fingerprint;
(d) detecting transient audio events and computing time differences of arrival among three or more such events to produce an ambient timestamp;
(e) exchanging said hash chain and said ambient timestamp among said devices using a gossip protocol without exchanging raw audio;
(f) applying a deterministic function to the set of exchanged hash chains to derive a shared context identifier; and
(g) outputting said context identifier on each device.
