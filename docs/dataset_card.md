# Dataset card

- Name: NirikshaID Synthetic v1.0.0
- Size: 600 locally generated images
- Language: English
- Layouts: one original fictional design
- Identities: entirely synthetic
- Photos: procedural geometric avatars
- Fields: five
- Tampers: none, font swap, copy/paste splice, digit edit
- Degradations: blur, Gaussian noise, JPEG
- Intended use: controlled research evaluation and engineering demonstrations
- Excluded use: identity verification, security decisions, or claims about real-world fraud

The generator can replay every document from the stored seed. Validation reports live under `data/generated/manifests`.

Diagnostic v1.1 is stored separately under `data/diagnostics`. It contains 30 counterfactual pairs (60 images) and 40 hard-negative genuine images. This separation prevents the base benchmark version from changing silently.
