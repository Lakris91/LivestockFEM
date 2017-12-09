function BygFEM_ramme
%% Program til statisk beregning af 2D rammekonstruktioner
clear all; close all

% knudekoordinater: X(knude,:)=[x,y] 
MatLabNodes   
% number of nodes, antal knuder i systemet

% elementer: T(el,:)=[startknude slutknude]        
MatLabElements  
% number of elements, antal elementer i systemet

% frihedsgrader, globale dof: D(el,:)=[V1 V2 V3 V4 V5 V6]
MatLabDOFS  
% number of dofs, antal frihedsgrader

% materialer: G(el,:)=[E-modul, tværsnitsareal, inertimoment]
MatLabMaterial

% understøtninger: U(i)=global dof
MatLabSupport

% knudelaste (boundary Load): bL(i,:)=[global_dof, størrelse]
MatLabNodeLoads

% elementlaste (domain Load): dL(el,:)=[lokal_retning, størrelse]
MatLabElementLoad

% skalering af plot
Vskala = PlotScalingDeformation;       % deformationer
Sskala = PlotScalingForces;    % snitkræfter

%% PROGRAM 

% plot geometrien
plotTop(X,T,nel,nno)

% Opstil systemstivhedsmatrix K
K = zeros(nd,nd);                      % initialisering af K
for el = 1:nel
  no1 = T(el,1);  no2 = T(el,2);       % startknude/slutknude
  X1 = X(no1,:);  X2 = X(no2,:);       % koordinater til start-/slutknude
  k = kbeam(X1,X2,G(el,:));            % stivhedsmatrix for element
  de = D(el,:);                        % knudeflytningsnumre, indexarray
  K(de,de) = K(de,de) + k;             % k lægges til K
end

% Opstil lastvektor R
R = zeros(nd,1);                       % initialiser R
for el = 1:nel
  dLe = dL(el,:);
  if dLe(1) > 0
    no1 = T(el,1);  no2 = T(el,2);     % startknude/slutknude
    X1 = X(no1,:);  X2 = X(no2,:);     % koordinater til start-/slutknude
    r = rbeam(X1,X2,dLe);              % elementlastvektor
    de = D(el,:);                      % knudeflytningsnumre, indexarray
    R(de) = R(de) + r;                 % r lægges til R
  end
end
nbL = size(bL,1);                      % antal knudelaste
for i = 1:nbL
  d = bL(i,1);                         % global dof med knudelast
  R(d) = R(d) + bL(i,2);               % knudelast lægges til R 
end

% Løs FEM-ligninger
dof = 1:nd;                      % indeks til alle knudeflytninger 
du = U;                          % indeks til foreskrevne knudeflytninger
df = setdiff(dof,du);            % indeks til frie knudeflytninger
Kff = K(df,df);
Kuu = K(du,du);
Kfu = K(df,du);
V = zeros(nd,1);                 % nulstil knudeflytningsvektor
Vu = V(du);                      % foreskrevne knudeflytninger
Rf = R(df);                      % belastninger
Vf = Kff\(Rf-Kfu*Vu);            % frie knudeflytninger
Ru = Kfu'*Vf+Kuu*Vu;             % reaktioner
V(df) = Vf;
V(du) = Vu;
disp('Flytninger:'); V = V       % udskriv flytninger
disp('Reaktioner:'); Ru = Ru     % udskriv rekationer
plotDof(X,T,D,V,nel,Vskala)      % plot deformeret gitter

% Beregn snitkræfter 
for el = 1:nel
    no1 = T(el,1);  no2 = T(el,2);     % startknude/slutknude
    X1 = X(no1,:);  X2 = X(no2,:);     % koordinater til start-/slutknude
    de = D(el,:);                      % indexarray
    [f1 f2 m] = S(X1,X2,G(el,:),V(de),dL(el,:));  % beregn snitkræfter
    F1(el,:) = f1;
    F2(el,:) = f2;
    M(el,:) = m;
end

disp('Normalkræfter:'); F1 = F1
disp('Forskydningskræfter:'); F2 = F2
disp('Momenter:'); M = M

fileID = fopen('result.txt','w');
fprintf(fileID,'%0.4f,',V);
fprintf(fileID,'/');
fprintf(fileID,'%0.4f,',Ru);
fprintf(fileID,'/');
fprintf(fileID,'%0.4f,',F1);
fprintf(fileID,'/');
fprintf(fileID,'%0.4f,',F2);
fprintf(fileID,'/');
fprintf(fileID,'%0.4f,',M);
fclose(fileID);

plotS(X,T,nel,F1,1,dL,Sskala)
plotS(X,T,nel,F2,2,dL,Sskala)
plotS(X,T,nel,M,3,dL,Sskala)

end % BygFEM_ramme

%% FUNKTIONER

function k = kbeam(X1,X2,G)
% Opstil elementstivhedsmatrix 
% dan transformationsmatrix
[A L] = Abeam(X1,X2);
% dan k efter lokale retninger
EA = G(1)*G(2);
EI = G(1)*G(3);
k = [ EA/L     0         0     -EA/L      0         0
       0   12*EI/L^3  6*EI/L^2   0   -12*EI/L^3  6*EI/L^2
       0    6*EI/L^2  4*EI/L     0    -6*EI/L^2  2*EI/L
     -EA/L     0         0      EA/L      0         0
       0  -12*EI/L^3 -6*EI/L^2   0    12*EI/L^3 -6*EI/L^2
       0    6*EI/L^2  2*EI/L     0    -6*EI/L^2  4*EI/L   ];
% transformer k til glabale retninger
k = A'*k*A;
end

function r = rbeam(X1,X2,dLe)
% Opstil elementlastvektor 
% dan transformationsmatrix
[A L] = Abeam(X1,X2);
% opstil r efter lokale retninger
r = zeros(6,1);
if dLe(1) == 1
  p = dLe(2)*L/2;
  r = [p 0 0 p 0 0]';
elseif dLe(1) == 2
  p = dLe(2)*L/2;
  m = dLe(2)*L^2/12;
  r = [0 p m 0 p -m]';
else
  disp('Fejl i specifikation af last!')
end
r = A'*r;
end

function [f1 f2 m] = S(X1,X2,Ge,Ve,dLe)
% Beregn snitkræfter i element: 
% f1: normalkraft 
% f2: forskydningskraft
% m:  moment 
% dan transformationsmatrix
[A L] = Abeam(X1,X2);
% dan elementstivhedsmatrix
k = kbeam(X1,X2,Ge);
% beregn lokal knudekraftvektor
re = A*k*Ve;
% opstil belastningsvektor efter lokale retninger
if dLe(1) == 2
  p = dLe(2)*L/2;
  m = dLe(2)*L^2/12;
  r = [0 p m 0 p -m]';
elseif dLe(1) == 1
  p = dLe(2)*L/2;
  r = [p 0 0 p 0 0]';
else
  r = [0 0 0 0 0 0]';
end
re = re-r;
f1 = [-re(1)  re(4)];
f2 = [ re(2) -re(5)];
m  = [-re(3)  re(6)];
end

function [A L] = Abeam(X1,X2)
% Beregn A 
n = X2-X1;                      % retningsvektor
L = sqrt(dot(n,n));             % elementlængde
n = n/L;                        % enhedsvektor
% dan transformationsmatrix
A = [ n(1) n(2)   0     0     0    0
     -n(2) n(1)   0     0     0    0
       0     0    1     0     0    0
       0     0    0    n(1) n(2)   0
       0     0    0   -n(2) n(1)   0
       0     0    0     0     0    1];
end

function plotTop(X,T,nel,nno)
% plot geometri
figure(); title('Elementtopologi'); axis equal; hold on
for el = 1:nel
  plot(X(T(el,:),1),X(T(el,:),2),'b-')
end
for no = 1:nno
  text(X(no,1),X(no,2),num2str(no),...
       'color','blue','BackgroundColor',[0.7 0.7 0.7]);
end
for el = 1:nel
  xp=mean(X(T(el,:),:));
  text(xp(1),xp(2),num2str(el),'color','black');
end
hold off
end

function plotDof(X,T,D,V,nel,skala)
% plot deformeret geometri (degrees of freedom)
figure(); axis equal; hold on 
title(['Deformationer, skala: ' num2str(skala, '%10.3e')]); 
fileID2 = fopen('deformation.txt','w');
for el = 1:nel
  plot(X(T(el,:),1),X(T(el,:),2),'b:')
  % deformeret
  % dan transformationsmatrix
  no1 = T(el,1);  no2 = T(el,2);       % startknude/slutknude
  X1 = X(no1,:);  X2 = X(no2,:);       % koordinater til start-/slutknude
  [A L] = Abeam(X1,X2);
  % dan transformationsmatrix for flytninger
  Au=A(1:2,1:2);
  % hent lokale flytninger
  v=V(D(el,:));
  % koordinater plus flytninger
  nrp=11;
  Xs=zeros(2,nrp);
  for i=1:nrp
    s=(i-1)/(nrp-1);
    N=[1-s             0               0 s           0            0;
       0   1-3*s^2+2*s^3 (s-2*s^2+s^3)*L 0 3*s^2-2*s^3 (-s^2+s^3)*L];
    Xs(:,i)=X(T(el,1),:)'*(1-s)+X(T(el,2),:)'*s+skala*Au'*N*A*v;
  end
  plot(Xs(1,:),Xs(2,:),'b-');
  
  fprintf(fileID2,'%0.4f,',Xs(1,:));
  fprintf(fileID2,'/');
  fprintf(fileID2,'%0.4f,',Xs(2,:));
  fprintf(fileID2,'/');
  fprintf(fileID2,'_');
end
fclose(fileID2);
hold off
end

function plotS(X,T,nel,S,s,dL,skala)
% plot snitkraft S
if s == 1
  sf = 'Normalkraft';
elseif s == 2
  sf = 'Forskydningskraft';
elseif s == 3
  sf = 'Moment';
else
  sf = ' ';
end
figure(); axis equal; hold on 
title([sf ', skala: ' num2str(skala, '%10.3e')]); 
for el = 1:nel
  n = X(T(el,2),:)-X(T(el,1),:);  % retningsvektor
  L = sqrt(dot(n,n));             % elementlængde
  n = n/L;                        % enhedsvektor
  plot(X(T(el,:),1),X(T(el,:),2),'b-')
  F1 = [-n(2) n(1)]*S(el,1)*skala;
  F2 = [-n(2) n(1)]*S(el,2)*skala;
  x1 = X(T(el,1),1);
  x2 = X(T(el,2),1);
  y1 = X(T(el,1),2);
  y2 = X(T(el,2),2);
  xm = (x1+x2)/2-n(2)*L/15;
  ym = (y1+y2)/2+n(1)*L/15;
  plot(xm,ym,'r+')
  if s == 3
    p = dL(el,2);
    m = -p*L^2/2;
    np = 9;             % antal mellempunkter
    Xp = zeros(np+4,1);
    Yp = zeros(np+4,1);
    Xp(1) =    x1;  Xp(2) =    x1+F1(1);
    Yp(1) =    y1;  Yp(2) =    y1+F1(2);
    Xp(np+4) = x2;  Xp(np+3) = x2+F2(1);
    Yp(np+4) = y2;  Yp(np+3) = y2+F2(2);
    for i = 1:np
      x = i/(np+1);
      mx = m*x*(1-x);
      m1 = [-n(2) n(1)]*mx*skala;
      Xp(i+2) = Xp(2)+i*(Xp(np+3)-Xp(2))/(np+1)+m1(1);
      Yp(i+2) = Yp(2)+i*(Yp(np+3)-Yp(2))/(np+1)+m1(2);
    end
  else
    Xp = [x1; x1+F1(1); x2+F2(1); x2];
    Yp = [y1; y1+F1(2); y2+F2(2); y2];
  end
  plot(Xp,Yp,'r-')
end
hold off
end
