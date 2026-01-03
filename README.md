# MicroPrime

**Experimental project for prime number exploration based on the GC-60 model**

---

## Overview

MicroPrime is an experimental project dedicated to the exploration of prime numbers through an arithmetic model called **GC-60**.

The goal of the project is not the exhaustive enumeration of primes, but the ability to **extract prime numbers efficiently inside arbitrary numeric windows**, provided that a suitable archive has been previously constructed.

MicroPrime is designed as an **incremental and persistent system**: once the archive is built, it can be extended over time without recomputing previously generated data.

---

## Core idea

The GC-60 model is based on a structural reduction of the natural numbers using admissible residue classes modulo 60.  
This reduction removes trivial composites in advance and allows the construction of a compact and structured archive of divisors.

A key design principle of MicroPrime is the **separation between archive construction and archive interrogation**:

- the archive encodes arithmetic information derived from the GC-60 model;
- prime numbers are extracted only when a specific numeric window is queried.

This approach differs from classical sieves and brute-force methods, which typically operate on a single contiguous range.

---

## GC-60 model overview

A conceptual overview of the GC-60 arithmetic model is available in the documentation folder.

The document describes the structural principles of GC-60 independently of any specific implementation, including:
- the use of admissible residue classes modulo 60;
- the concept of an incremental arithmetic archive;
- the idea of localized windows of exploration.

See:  
[`docs/GC_60_overview.tex`](docs/GC-60_overview.tex)

---

## Project structure

The repository is organized into three main components:

- **MicroPrimeV1/**  
  Responsible for building and incrementally extending the GC-60 archive.  
  The archive can be created from scratch or extended from the last valid state.

- **MicroPrime_studio/**  
  Provides tools to explore the archive, extract prime numbers inside user-defined windows, and compute basic statistical analyses.

- **docs/**  
  Contains conceptual documentation describing the GC-60 model and the overall architecture of the project.

---

## Incremental archive

One of the defining features of MicroPrime is its **incremental archive**.

The archive:
- grows monotonically over time;
- can be extended without invalidating previous data;
- allows the computation to be paused and resumed at any moment.

Each archive file represents a consistent and self-contained state.  
When additional capacity is required, MicroPrime continues from the last archive file instead of restarting the computation from the beginning.

This design makes long-term exploration feasible even on modest hardware.

---

## What MicroPrime does

- Builds an arithmetic archive based on the GC-60 model  
- Allows fast extraction of prime numbers in arbitrary numeric windows  
- Supports basic statistical analyses as a secondary, exploratory feature  

---

## What MicroPrime does not do

- It is **not** a general-purpose factorization algorithm  
- It does **not** claim optimal asymptotic complexity  
- It does **not** provide definitive statistical conclusions about prime distribution  

MicroPrime should be considered a **research and exploration tool**, not a closed or optimized final solution.

---

## Intended audience

MicroPrime is aimed at two types of users:

- **Enthusiasts**, who can use the software as-is to explore prime numbers;
- **Researchers and advanced users**, who are interested in understanding the GC-60 model and developing their own analyses on top of it.

The project encourages experimentation and independent interpretation of the data.

---

## Project status

MicroPrime is an active experimental project.

- The code is functional and tested  
- The archive system supports incremental growth  
- A more formal and mathematical description of the GC-60 model is planned for a future publication (e.g. Zenodo)

---

## License

This project is released under the MIT License.  
See the `LICENSE` file for details.
