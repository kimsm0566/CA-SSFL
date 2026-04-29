# Table 1 Updated Rayleigh Snippet

아래 코드는 현재 재실험 결과를 반영한 `Table 1`의 Rayleigh 기준 LaTeX 스니펫이다.

기준:
- 왼쪽 블록 `(\beta, \tau_{VIB})`: `seed 1,2,3,4`
- 오른쪽 블록 `(\tau_{max}, \tau_{min})`: `seed 1,2,3,4`
- 오른쪽 블록은 `beta=0.100`, `tau_{VIB}=1.0` 고정으로 다시 측정한 최신 값이다.

```latex
\begin{table}[t]
    \caption{Performance analysis of CA-SSFL on CIFAR-10 Rayleigh. The left block shows the correlation between $\beta$ and $\tau_{VIB}$ when $\tau_{max}$ and $\tau_{min}$ are fixed at $0.7$ and $0.4$, respectively. The right block shows the correlation between $\tau_{max}$ and $\tau_{min}$ when $\beta$ and $\tau_{VIB}$ are fixed at $0.100$ and $1.0$, respectively. (\textbf{B}: Best, \underline{U}: Second)}
    \label{table:ca_ssfl_ablation_single_rayleigh_updated}
    \centering
    \footnotesize
    \setlength{\tabcolsep}{4.5pt}
    
    \begin{tabular}{cc|cc||cc|cc}
    \toprule
    $\beta$ & $\tau_{VIB}$ & \makecell{Acc.\\(\%)} & \makecell{Comm.\\(GB)} &
    $\tau_{max}$ & $\tau_{min}$ & \makecell{Acc.\\(\%)} & \makecell{Comm.\\(GB)} \\
    \midrule
    
    \multirow{3}{*}{0.100}
        & 1.5 & 12.44 & \textbf{8.17} & \multirow{3}{*}{0.7} & 0.2 & 38.89 & 15.25 \\
        & 1.0 & \textbf{40.41} & 14.59 &                          & 0.3 & 39.38 & 15.09 \\
        & 0.5 & 38.09 & 17.62 &                          & 0.4 & \textbf{40.41} & 14.59 \\
    \cmidrule(lr){1-4} \cmidrule(lr){5-8}

    \multirow{3}{*}{0.050}
        & 1.5 & 14.58 & \underline{8.19} & \multirow{3}{*}{0.8} & 0.2 & 39.07 & 14.30 \\
        & 1.0 & 37.88 & 15.72 &                          & 0.3 & 39.36 & 13.94 \\
        & 0.5 & 38.24 & 19.76 &                          & 0.4 & 39.53 & 13.19 \\
    \cmidrule(lr){1-4} \cmidrule(lr){5-8}

    \multirow{3}{*}{0.010}
        & 1.5 & 31.11 & 9.16 & \multirow{3}{*}{0.9} & 0.2 & 38.80 & 13.37 \\
        & 1.0 & 39.50 & 19.16 &                        & 0.3 & 38.60 & \underline{13.02} \\
        & 0.5 & 36.74 & 27.52 &                        & 0.4 & \underline{39.62} & \textbf{12.48} \\
    \cmidrule(lr){1-4} \cmidrule(lr){5-8}

    \multirow{3}{*}{0.005}
        & 1.5 & 36.05 & 9.15 & \multicolumn{4}{c}{} \\
        & 1.0 & 38.14 & 20.81 & \multicolumn{4}{c}{} \\
        & 0.5 & 38.04 & 34.72 & \multicolumn{4}{c}{} \\
    \cmidrule(lr){1-4}

    \multirow{3}{*}{0.001}
        & 1.5 & 37.88 & 10.06 & \multicolumn{4}{c}{} \\
        & 1.0 & 38.55 & 25.81 & \multicolumn{4}{c}{} \\
        & 0.5 & 37.80 & 45.49 & \multicolumn{4}{c}{} \\
    \bottomrule
    \end{tabular}
\end{table}
```
