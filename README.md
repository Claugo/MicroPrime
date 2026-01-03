\documentclass[11pt,a4paper]{article}

\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{geometry}
\usepackage{hyperref}
\usepackage{enumitem}

\geometry{margin=2.5cm}

\title{\textbf{MicroPrime}\\
\large Experimental project for prime number exploration based on the GC-60 model}

\author{}
\date{}

\begin{document}

\maketitle

\section*{Overview}

MicroPrime is an experimental project dedicated to the exploration of prime numbers through an arithmetic model called \textbf{GC-60}.

The goal of the project is not the exhaustive enumeration of primes, but the ability to extract prime numbers efficiently inside arbitrary numeric windows, provided that a suitable archive has been previously constructed.

MicroPrime is designed as an \textbf{incremental and persistent system}: once the archive is built, it can be extended over time without recomputing previously generated data.

\section*{Core idea}

The GC-60 model is based on a structural reduction of the natural numbers using admissible residue classes modulo 60.
This reduction removes trivial composites in advance and allows the construction of a compact and structured archive of divisors.

A key design principle of MicroPrime is the separation between archive construction and archive interrogation:

\begin{itemize}[leftmargin=1.5cm]
\item the archive encodes arithmetic information derived from the GC-60 model;
\item prime numbers are extracted only when a specific numeric window is queried.
\end{itemize}

This approach differs from classical sieves and brute-force methods, which typically operate on a single contiguous range.

# GC-60 model overview

A conceptual overview of the GC-60 arithmetic model is available in the documentation folder.

The document describes the structural principles of GC-60 independently of any specific implementation, including:

- the use of admissible residue classes modulo 60;
- the concept of an incremental arithmetic archive;
- the idea of localized windows of exploration.

\section*{Project structure}

The project is organized into three main components:

\begin{itemize}[leftmargin=1.5cm]
\item \textbf{MicroPrimeV1} \\
Responsible for building and incrementally extending the GC-60 archive.  
The archive can be created from scratch or extended from the last valid state.

\item \textbf{MicroPrime\_studio} \\
Provides tools to explore the archive, extract prime numbers inside user-defined windows, and compute basic statistical analyses.

\item \textbf{docs} \\
Contains conceptual documentation describing the GC-60 model and the overall architecture of the project.
\end{itemize}

\section*{Incremental archive}

One of the defining features of MicroPrime is its \textbf{incremental archive}.

The archive:
\begin{itemize}[leftmargin=1.5cm]
\item grows monotonically over time;
\item can be extended without invalidating previous data;
\item allows the computation to be paused and resumed at any moment.
\end{itemize}

Each archive file represents a consistent and self-contained state.
When additional capacity is required, MicroPrime continues from the last archive file instead of restarting the computation from the beginning.

This design makes long-term exploration feasible even on modest hardware.

\section*{What MicroPrime does}

\begin{itemize}[leftmargin=1.5cm]
\item Builds an arithmetic archive based on the GC-60 model;
\item Allows fast extraction of prime numbers in arbitrary numeric windows;
\item Supports basic statistical analyses (density, gaps, modulo 60 distribution) as a secondary, exploratory feature.
\end{itemize}

\section*{What MicroPrime does not do}

\begin{itemize}[leftmargin=1.5cm]
\item It is not a general-purpose factorization algorithm;
\item It does not claim optimal asymptotic complexity;
\item It does not provide definitive statistical conclusions about prime distribution.
\end{itemize}

MicroPrime should be considered a \textbf{research and exploration tool}, not a closed or optimized final solution.

\section*{Intended audience}

MicroPrime is aimed at two types of users:

\begin{itemize}[leftmargin=1.5cm]
\item \textbf{Enthusiasts}, who can use the software as-is to explore prime numbers;
\item \textbf{Researchers and advanced users}, who are interested in understanding the GC-60 model and developing their own analyses on top of it.
\end{itemize}

The project encourages experimentation and independent interpretation of the data.

\section*{Project status}

MicroPrime is an active experimental project.

\begin{itemize}[leftmargin=1.5cm]
\item The code is functional and tested;
\item The archive system supports incremental growth;
\item A more formal and mathematical description of the GC-60 model is planned for a future publication (e.g.\ Zenodo).
\end{itemize}

\section*{License}

MicroPrime is released under the MIT License.
Refer to the \texttt{LICENSE} file in the repository for full license terms.

\end{document}
