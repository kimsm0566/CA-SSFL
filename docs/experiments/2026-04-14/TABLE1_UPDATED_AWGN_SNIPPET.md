# Table 1 Updated AWGN Snippet

아래 코드는 현재 재실험 결과를 반영한 `Table 1`의 AWGN 기준 LaTeX 스니펫이다.

기준:
- 왼쪽 블록 `(\beta, \tau_{VIB})`: `seed 1,2,3,4`
- 오른쪽 블록 `(\tau_{max}, \tau_{min})`: `seed 1,2,3,4`
- 오른쪽 블록은 `beta=0.050`, `tau_{VIB}=1.0` 고정으로 다시 측정한 최신 값이다.

```latex
\begin{table}[t]
    \caption{Performance analysis of CA-SSFL on CIFAR-10 AWGN. The left block shows the correlation between $\beta$ and $\tau_{VIB}$ when $\tau_{max}$ and $\tau_{min}$ are fixed at $0.7$ and $0.4$, respectively. The right block shows the correlation between $\tau_{max}$ and $\tau_{min}$ when $\beta$ and $\tau_{VIB}$ are fixed at $0.050$ and $1.0$, respectively. (\textbf{B}: Best, \underline{U}: Second)}
    \label{table:ca_ssfl_ablation_single_updated}
    \centering
    \footnotesize
    \setlength{\tabcolsep}{4.5pt}
    
    \begin{tabular}{cc|cc||cc|cc}
    \toprule
    $\beta$ & $\tau_{VIB}$ & \makecell{Acc.\\(\%)} & \makecell{Comm.\\(GB)} &
    $\tau_{max}$ & $\tau_{min}$ & \makecell{Acc.\\(\%)} & \makecell{Comm.\\(GB)} \\
    \midrule
    
    \multirow{3}{*}{0.100}
        & 1.5 & 20.34 & \underline{8.22} & \multirow{3}{*}{0.7} & 0.2 & \textbf{41.71} & 14.03 \\
        & 1.0 & 39.41 & 12.63 &                          & 0.3 & 40.70 & 14.05 \\
        & 0.5 & 40.20 & 15.51 &                          & 0.4 & 41.39 & 13.41 \\
    \cmidrule(lr){1-4} \cmidrule(lr){5-8}

    \multirow{3}{*}{0.050}
        & 1.5 & 16.57 & \textbf{8.19} & \multirow{3}{*}{0.8} & 0.2 & 40.44 & 13.23 \\
        & 1.0 & \textbf{41.39} & 13.41 &                          & 0.3 & 39.80 & 12.85 \\
        & 0.5 & 39.82 & 17.39 &                          & 0.4 & \underline{41.53} & 12.52 \\
    \cmidrule(lr){1-4} \cmidrule(lr){5-8}

    \multirow{3}{*}{0.010}
        & 1.5 & 32.38 & 8.66 & \multirow{3}{*}{0.9} & 0.2 & 40.08 & 12.64 \\
        & 1.0 & 40.46 & 15.87 &                        & 0.3 & 40.83 & \underline{12.05} \\
        & 0.5 & 37.66 & 24.05 &                        & 0.4 & 41.27 & \textbf{11.55} \\
    \cmidrule(lr){1-4} \cmidrule(lr){5-8}

    \multirow{3}{*}{0.005}
        & 1.5 & 32.69 & 9.27 & \multicolumn{4}{c}{} \\
        & 1.0 & 40.83 & 17.12 & \multicolumn{4}{c}{} \\
        & 0.5 & 40.69 & 31.12 & \multicolumn{4}{c}{} \\
    \cmidrule(lr){1-4}

    \multirow{3}{*}{0.001}
        & 1.5 & 39.04 & 9.63 & \multicolumn{4}{c}{} \\
        & 1.0 & \underline{40.98} & 20.59 & \multicolumn{4}{c}{} \\
        & 0.5 & 38.20 & 39.41 & \multicolumn{4}{c}{} \\
    \bottomrule
    \end{tabular}
\end{table}
```
