      PROGRAM BATTLE

      INTEGER GA, GB, NWA, NWB, FIRECA(20), FIRECB(20), DURCA(20),
     +DURCB(20), FIREPA(20), FIREPB(20), NFAP, NFBP, SHTPA(10),
     +SHTPB(10), NBPF(10), NAPF(10), IMPA(20), IMPB(20), TGTPA(20,10),
     +TGTPB(20,10), PA, PB, JPA, JPB, NFA(10), NFB(10), SHTCA(20,10),
     +SHTCB(20,10), NACF(10), NBCF(10), TGTCA(20,10), TGTCB(20,10),
     +STOPCA(20), STOPCB(20), CA, JCA, CB, JCB, A, G, H, HA, HB, I, K,
     + L1, M, N

      REAL SA(10), SB(10), SA0, SB0, FCA(10), FCB(10), FPA(10,10),
     +FPB(10,10), PCA(10), PCB(10), TOTPFP, PULSEA(20), PULSEB(20),
     +PPA(20), PPB(20), LA(10), LB(10), SP, LPA(10), LPB(10), LCA(10),
     +LCB(10), L, FC, SATOT, SBTOT, FCATOT, FCBTOT, FPATOT, FPBTOT,
     +TLSA, TLSB, TLCA, TLCB, TLPA, TLPB, FPA0, FPB0, FCA0, FCB0,
     +BPA, BPB

      DATA FIRECA,FIRECB,DURCA,DURCB /20*0, 20*0, 20*0, 20*0/
      DATA FIREPA,FIREPB,NBPF,NAPF /20*0,20*0,10*0,10*0/
      DATA IMPA,IMPB,NFA,NFB,NACF /20*0,20*0,10*0,10*0,10*0/
      DATA NBCF,STOPCA,STOPCB,SHTPA /10*0,20*0,20*0,10*0/
      DATA SHTPB,SA,SB,FCA,FCB /10*0,10*0,10*0,10*0,10*0/
      DATA PCA,PCB,LA,LB,LPA /10*0,10*0,10*0,10*0,10*0/
      DATA LPB,LCA,LCB,PULSEA,PULSEB /10*0,10*0,10*0,20*0,20*0/
      DATA PPA,PPB /20*0,20*0/
      DATA SHTCA,SHTCB,TGTCA,TGTCB /200*0,200*0,200*0,200*0/
      DATA FPA,FPB /100*0,100*0/

      SA0 = 0
      SB0 = 0
      FCA0 = 0
      FCB0 = 0
      FPA0 = 0
      FPB0 = 0

      PRINT*, 'ENTER THE FOLLOWING:'
      PRINT*
      PRINT*, 'NUMBER OF GROUPS INTO WHICH A AND B ARE DIVIDED.'
      READ*, GA, GB
      PRINT*, 'STAYING POWER OF EACH A GROUP.'
      READ*, (SA(I), I = 1, GA)
      PRINT*, 'STAYING POWER OF EACH B GROUP.'
      READ*, (SB(I), I = 1, GB)
      DO 10 I = 1, GA
          SA0 = SA0 + SA(I)
10    CONTINUE
      DO 20 I = 1, GB
          SB0 = SB0 + SB(I)
20    CONTINUE
      PRINT*, 'THEORETICAL CONTINUOUS COMBAT POWER OF EACH A GROUP.'
      DO 21 I = 1, GA
          READ*, FCA(I)
          FCA0 = FCA0 + FCA(I)
21    CONTINUE
      PRINT*, 'THEORETICAL CONTINUOUS COMBAT POWER OF EACH B GROUP.'
      DO 22 I = 1, GB
          READ*, FCB(I)
          FCB0 = FCB0 + FCB(I)
22    CONTINUE
      PRINT*, 'NUMBER OF PULSED WEAPONS TYPES IN FORCES A AND B.'
      READ*, NWA, NWB
      IF (NWA.EQ.0) GOTO 30
      PRINT*, 'THEORETICAL PULSE COMBAT POWER'
      PRINT*, 'OF EACH PULSE WEAPON IN A:'
      PRINT*
      DO 30 I = 1, GA
          PRINT*, 'GROUP ', I
          DO 23 J = 1, NWA
              READ*, FPA(I, J)
              FPA0 = FPA0 + FPA(I, J)
23        CONTINUE
30    CONTINUE
      IF (NWB.EQ.0) GOTO 45
      PRINT*, 'THEORETICAL PULSE COMBAT POWER'
      PRINT*, 'OF EACH PULSE WEAPON IN B:'
      PRINT*
      DO 40 I = 1, GB
          PRINT*, 'GROUP ', I
          DO 31 J = 1, NWB
              READ*, FPB(I, J)
              FPB0 = FPB0 + FPB(I, J)
31        CONTINUE
40    CONTINUE
      
45    PRINT*, 'DOES THIS ENGAGEMENT INCLUDE CONTINUOUS FIRE?'
      PRINT*, '(1 IF YES, 0 IF NO)'
      READ*, A
      IF (A.EQ.0) GOTO 80
      PRINT*, 'ENTER CONTINUOUS WEAPON EFFECTIVENESS'
      PRINT*, 'FOR EACH A GROUP.'
      READ*, (PCA(I), I = 1, GA)
      PRINT*, 'ENTER CONTINUOUS WEAPON EFFECTIVENESS'
      PRINT*, 'FOR EACH B GROUP.'
      READ*, (PCB(I), I = 1, GB)
      PRINT*, 'ENTER THE NUMBER OF TIMES A WILL EMPLOY'
      PRINT*, 'CONTINUOUS FIRE (INCLUDING 0).'
      READ*, M
      IF (M.LE.0) GOTO 60
      PRINT*, 'ENTER THE INCREMENTS AT WHICH A WILL OPEN'
      PRINT*, 'CONTINUOUS FIRE AND THE DURATION OF FIRE.'
      DO 50 I = 1, M
           READ*, FIRECA(I), DURCA(I)
50    CONTINUE
60    PRINT*, 'ENTER THE NUMBER OF TIMES B WILL EMPLOY'
      PRINT*, 'CONTINUOUS FIRE (INCLUDING 0).'
      READ*, M
      IF (M.LE.0) GOTO 80
      PRINT*, 'ENTER THE INCREMENTS AT WHICH B WILL OPEN'
      PRINT*, 'CONTINUOUS FIRE AND THE DURATION OF FIRE.'
      DO 70 I = 1, M
          READ*, FIRECB(I), DURCB(I)
70    CONTINUE
80    PRINT*, 'DOES THIS ENGAGEMENT INCLUDE PULSED FIRE?'
      PRINT*, '(1 IF YES, 0 IF NO).'
      READ*, A
      IF (A.EQ.0) GOTO 100
      PRINT*, 'ENTER THE NUMBER OF TIMES A WILL FIRE (INCLUDING 0).'
      READ*, M
      IF (M.EQ.0) GOTO 90
      PRINT*, 'ENTER THE TIME INCREMENTS AT WHICH A WILL OPEN FIRE.'
      READ*, (FIREPA(I), I = 1, M)
90    PRINT*, 'ENTER THE NUMBER OF TIMES B WILL FIRE (INCLUDING 0).'
      READ*, M
      IF (M.EQ.0) GOTO 100
      PRINT*, 'ENTER THE TIME INCREMENTS AT WHICH B WILL OPEN FIRE.'
      READ*, (FIREPB(I), I = 1, M)
      
100   PRINT*, 'DO YOU WISH TO KNOW:'
      PRINT*
      PRINT*, 'THE RESULTS OF THE BATTLE AFTER A GIVEN NUMBER OF'
      PRINT*, 'INCREMENTS? (1 IF YES, 0 IF NO).'
      READ*, A
      IF(A.EQ.1) GOTO 110
      PRINT*, 'THE OUTCOME OF A FIGHT TO A PREDETERMINED'
      PRINT*, '% LOSS IN STAYING POWER?'
      PRINT*, '(1 IF YES, 0 IF NO).'
      READ*, A
      IF (A.EQ.1) GOTO 120
      STOP
      
110   PRINT*, 'ENTER THE NUMBER OF INCREMENTS TO BE CONSIDERED.'
      READ*, N
      BPA = 2 - 3
      BPB = 2 - 3
      GOTO 121
      
120   N = 1000
      PRINT*, 'ENTER THE MAXIMUM PERMISSIBLE % LOSS IN STAYING'
      PRINT*, 'POWER OF FORCE A.'
      READ*, BPA
      BPA = SA0 - ((BPA / 100) * SA0)
      PRINT*, 'ENTER THE MAXIMUM PERMISSIBLE % LOSS IN STAYING'
      PRINT*, 'POWER OF FORCE B.'
      READ*, BPB
      BPB = SB0 - ((BPB / 100) * SB0)
      
121   WRITE (7,130) 'INITIAL STRENGTH',SA0,FCA0,FPA0,SB0,FCB0,FPB0,
     + 'FORCE STRENGTH AT EACH ITERATION'
130   FORMAT (1X,A16//5X,'SA',4X,'FCA',4x,'FPA',5X,'SB',4X,'FCB',4X
     +,'FPB'/42('_')//1X,6(F6.2,1X)//1X,A32//4X,'I',7X,'SA',6X,'FCA',6X
     +,'FPA',7X,'SB',6X,'FCB',6X,'FPB'/59('_')//)
      TOTPFP = 0
      PA     = 1
      JPA    = 1
      PB     = 1
      JPB    = 1
      CA     = 1
      JCA    = 1
      CB     = 1
      JCB    = 1
      HA     = 1
      HB     = 1
      SP     = 0
      L      = 0
      FC     = 0
      FCATOT = 0
      FCBTOT = 0
      FPATOT = 0
      FPBTOT = 0
      SATOT  = 0
      SBTOT  = 0
      
      DO 390 I = 1, N
      
140       IF (FIREPA(JPA).EQ.I) THEN
              PRINT*, 'FORCE A IS FIRING A PULSE.'
              PRINT*, 'HOW MANY INCREMENTS UNTIL IT REACHES ITS TARGET?'
              READ*, K
              PRINT*, 'HOW MANY GROUPS OF FORCE A ARE FIRING?'
              READ*, NFAP
              PRINT*, 'WHICH GROUPS ARE FIRING?'
              READ*, (SHTPA(H), H = 1, NFAP)
              PRINT*, 'WHICH PULSED WEAPON TYPE IS TO BE FIRED?'
              READ*, L1
              DO 145 H = 1, NFAP
                  TOTPFP = TOTPFP + FPA(SHTPA(H), L1)
145           CONTINUE
              PRINT*, 'THESE GROUPS CAN FIRE ', TOTPFP, ' UNITS.'
              PRINT*, 'HOW MANY UNITS ARE THEY GOING TO FIRE?'
              READ*, PULSEA(PA)
              PRINT*, 'WHAT IS THE WEAPON EFFECTIVENESS OF THIS PULSE?'
              READ*, PPA(PA)
              PRINT*, 'HOW MANY GROUPS OF FORCE B ARE BEING FIRED UPON?'
              READ*, NBPF(PA)
              PRINT*, 'WHICH GROUPS ARE BEING FIRED UPON?'
              READ*, (TGTPA(PA,H), H = 1, NBPF(PA))
              IMPA(PA) = I + K - 1
              TOTPFP = 0
              PA = PA + 1
              JPA = JPA + 1
              GOTO 140
          END IF
          
150       IF (FIREPB(JPB).EQ.I) THEN
              PRINT*, 'FORCE B IS FIRING A PULSE.'
              PRINT*, 'HOW MANY INCREMENTS UNTIL IT REACHES ITS TARGET?'
              READ*, K
              PRINT*, 'HOW MANY GROUPS OF FORCE B ARE FIRING?'
              READ*, NFBP
              PRINT*, 'WHICH GROUPS ARE FIRING?'
              READ*, (SHTPB(H), H = 1, NFBP)
              PRINT*, 'WHICH PULSED WEAPON TYPE IS TO BE FIRED?'
              READ*, L1
              DO 155 H = 1, NFBP
                  TOTPFP = TOTPFP + FPB(SHTPB(H), L1)
155           CONTINUE
              PRINT*, 'THESE GROUPS CAN FIRE ', TOTPFP, ' UNITS.'
              PRINT*, 'HOW MANY UNITS ARE THEY GOING TO FIRE?'
              READ*, PULSEB(PB)
              PRINT*, 'WHAT IS THE WEAPON EFFECTIVENESS OF THIS PULSE?'
              READ*, PPB(PB)
              PRINT*, 'HOW MANY GROUPS OF FORCE A ARE BEING FIRED UPON?'
              READ*, NAPF(PB)
              PRINT*, 'WHICH GROUPS ARE BEING FIRED UPON?'
              READ*, (TGTPB(PB,H), H = 1, NAPF(PB))
              IMPB(PB) = I + K - 1
              TOTPFP = 0
              PB = PB + 1
              JPB = JPB + 1
              GOTO 150
          END IF
          
160       IF (FIRECA(JCA).EQ.I) THEN
              PRINT*, 'FORCE A IS COMMENCING CONTINUOUS FIRE.'
              PRINT*, 'HOW MANY GROUPS ARE FIRING?'
              READ*, NFA(CA)
              PRINT*, 'WHICH GROUPS ARE FIRING?'
              READ*, (SHTCA(CA,H), H = 1, NFA(CA))
              PRINT*, 'HOW MANY GROUPS OF FORCE B ARE BEING FIRED UPON?'
              READ*, NBCF(CA)
              PRINT*, 'WHICH GROUPS ARE BEING FIRED UPON?'
              READ*, (TGTCA(CA,H), H = 1, NBCF(CA))
              STOPCA(CA) = I + (DURCA(JCA) - 1)
              CA = CA + 1
              JCA = JCA + 1
              GOTO 160
          END IF
          
170       IF (FIRECB(JCB).EQ.I) THEN
              PRINT*, 'FORCE B IS COMMENCING CONTINUOUS FIRE.'
              PRINT*, 'HOW MANY GROUPS ARE FIRING?'
              READ*, NFB(CB)
              PRINT*, 'WHICH GROUPS ARE FIRING?'
              READ*, (SHTCB(CB, H), H = 1, NFB(CB))
              PRINT*, 'HOW MANY GROUPS OF FORCE A ARE BEING FIRED UPON?'
              READ*, NACF(CB)
              PRINT*, 'WHICH GROUPS ARE BEING FIRED UPON?'
              READ*, (TGTCB(CB,H), H = 1, NACF(CB))
              STOPCB(CB) = I + (DURCB(JCB) - 1)
              CB = CB + 1
              JCB = JCB + 1
              GOTO 170
          END IF
          
          DO 180 H = 1, GA
              LCA(H) = 0
              LPA(H) = 0
180       CONTINUE
          DO 190 H = 1, GB
              LCB(H) = 0
              LPB(H) = 0
190       CONTINUE

200       IF (IMPA(HA).EQ.I) THEN
              DO 210 H = 1, NBPF(HA)
                  SP = SP + SB(TGTPA(HA, H))
210           CONTINUE
              CALL PFIRE(L, SP, PPA(HA), PULSEA(HA))
              DO 220 H = 1, NBPF(HA)
                  LPB(TGTPA(HA,H)) = LPB(TGTPA(HA,H)) + L
220           CONTINUE
              HA = HA + 1
              SP = 0
              L = 0
              GOTO 200
          END IF

230       IF (IMPB(HB).EQ.I) THEN
              DO 240 H = 1, NAPF(HB)
                  SP = SP + SA(TGTPB(HB, H))
240           CONTINUE
              CALL PFIRE(L, SP, PPB(HB), PULSEB(HB))
              DO 250 H = 1, NAPF(HB)
                  LPA(TGTPB(HB,H)) = LPA(TGTPB(HB,H)) + L
250           CONTINUE
              HB = HB + 1
              SP = 0
              L = 0
              GOTO 230
          END IF
          
          DO 290 H = 1, CA
              IF (STOPCA(H).GE.I) THEN
                  DO 260 G = 1, NFA(H)
                      FC = FC + FCA(SHTCA(H,G)) * PCA(SHTCA(H,G))
260               CONTINUE
                  DO 270 G = 1, NBCF(H)
                      SP = SP + SB(TGTCA(H,G))
270               CONTINUE
                  CALL CFIRE(L, SP, FC)
                  DO 280 G = 1, NBCF(H)
                      LCB(TGTCA(H,G)) = LCB(TGTCA(H,G)) + L
280               CONTINUE
                  FC = 0
                  SP = 0
                  L = 0
              END IF
290       CONTINUE

          DO 330 H = 1, CB
              IF (STOPCB(H).GE.I) THEN
                  DO 300 G = 1, NFB(H)
                      FC = FC + FCB(SHTCB(H,G)) * PCB(SHTCB(H,G))
300               CONTINUE
                  DO 310 G = 1, NACF(H)
                      SP = SP + SA(TGTCB(H,G))
310               CONTINUE
                      CALL CFIRE(L, SP, FC)
                  DO 320 G = 1, NACF(H)
                      LCA(TGTCB(H,G)) = LCA(TGTCB(H,G)) + L
320               CONTINUE
                  FC = 0
                  SP = 0
                  L = 0
              END IF
330       CONTINUE      

          DO 350 H = 1, GA
              LA(H) = LCA(H) + LPA(H)
              IF (LA(H).GT.1) LA(H) = 1
              CALL TOTATT (LA(H), FCA(H), SA(H))
              DO 340, G = 1, NWA
                  CALL PULATT(LA(H), FPA(H,G))
                  FPATOT = FPATOT + FPA(H, G)
340           CONTINUE
              SATOT = SATOT + SA(H)
              FCATOT = FCATOT + FCA(H)
350       CONTINUE

          DO 370 H = 1, GB
              LB(H) = LCB(H) + LPB(H)
              IF (LB(H).GT.1) LB(H) = 1
              CALL TOTATT (LB(H), FCB(H), SB(H))
              DO 360, G = 1, NWB
                  CALL PULATT(LB(H), FPB(H,G))
                  FPBTOT = FPBTOT + FPB(H,G)
360           CONTINUE
              SBTOT = SBTOT + SB(H)
              FCBTOT = FCBTOT + FCB(H)
370       CONTINUE

          WRITE(7,380) I, SATOT, FCATOT, FPATOT, SBTOT, FCBTOT, FPBTOT
380       FORMAT (1X, I4, 6(2X, F7.3))

          IF ((STATOT.LE.BPA).OR.(SBTOT.LE.BPB)) GOTO 395
          IF (I.EQ.N) GOTO 395
          
          FCATOT = 0
          FCBTOT = 0
          FPATOT = 0
          FPBTOT = 0
          SATOT = 0
          SBTOT = 0
          
390   CONTINUE

395   TLSA = (1 - (SATOT/SA0)) * 100
      TLSB = (1 - (SBTOT/SB0)) * 100
      IF (FCA0.GT.0) THEN
          TLCA = (1 - (FCATOT / FCA0)) * 100
      ELSE
          TLCA = 0
      END IF
      IF (FCB0.GT.0) THEN
          TLCB = (1 - (FCBTOT / FCB0)) * 100
      ELSE
          TLCB = 0
      END IF
      IF (FPA0.GT.0) THEN
          TLPA = (1 - (FPATOT/FPA0)) * 100
      ELSE
          TLPA = 0
      END IF
      IF (FPB0.GT.0) THEN
          TLPB = (1 - (FPBTOT/FPB0)) * 100
      ELSE
          TLPB = 0
      END IF
      
      PRINT*
      
      WRITE (6, 400) 'SUMMARY OF LOSSES (% LOST)',TLSA,TLCA,TLPA,TLSB,
     +TLCB, TLPB
      WRITE (7, 400) 'SUMMARY OF LOSSES (% LOST)', TLSA,TLCA,TLPA,TLSB,
     +TLCB,TLPB
400   FORMAT (/1X,A26//5X,'SA',4X,'FCA',4X,'FPA',5X,'SB',4X,'FCB',4X,
     + 'FPB'/1X,42('_')//1X,6(F6.2,1X))
     
      PRINT*
      
      END
      
      SUBROUTINE CFIRE(L, SP, FC)
      REAL L, SP, FC
      IF (SP.GT.0) THEN
          L = FC / SP
      ELSE
          L = 0
      END IF
      RETURN
      END
      
      SUBROUTINE PFIRE(L, SP, PP, PULSE)
      REAL L, SP, PP, PULSE
      IF (SP.GT.0) THEN
          L = (PULSE*PP)/SP
      ELSE
          L = 0
      END IF
      RETURN
      END
      
      SUBROUTINE TOTATT(L, FC, S)
      REAL L, FC, S
      FC = FC * (1 - L)
      S = S * (1 - L)
      RETURN
      END
      
      SUBROUTINE PULATT(L, FP)
      REAL L, FP
      FP = FP * (1 - L)
      RETURN
      END
