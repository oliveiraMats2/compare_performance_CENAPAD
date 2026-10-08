% Instituto de Computação - Unicamp
% LaTeX document class for theses and dissertations.
% ic-tese-v3 2018-10-17

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{ic-tese-v3}[]
\typeout{ic-tese-v3}

\def\thesislanguage#1{\gdef\@thesislanguage{#1}}
\DeclareOption{Ingles}{
  \thesislanguage{0}
  \typeout{ic-tese: ingles.}
}
\DeclareOption{Espanhol}{
  \thesislanguage{1}
  \typeout{ic-tese: espanhol.}
}
\DeclareOption{Portugues}{
  \thesislanguage{2}
  \typeout{ic-tese: portugues.}
}
\newif\iffinalversion
\DeclareOption{Final}{
  \finalversiontrue
  \typeout{ic-tese: versao final.}
}


\ProcessOptions\relax

\LoadClass[11pt,letterpaper]{article}

\RequirePackage[english,spanish,brazil]{babel}
\usepackage[T1]{fontenc}
\RequirePackage{graphicx}
\PassOptionsToPackage{table}{xcolor}
\RequirePackage{pdfpages}
\RequirePackage{logo-ic-unicamp}
\RequirePackage{xspace}

\RequirePackage{setspace}
\RequirePackage{geometry}
\geometry{a4paper,top=30mm,bottom=20mm,left=30mm,right=20mm}

\RequirePackage{fancyhdr}

\newcommand{\@IC}{Instituto de Computa\c{c}\~ao}
\newcommand{\@UNICAMP}{Universidade Estadual de Campinas}

% User fields:
\let\@autor\relax
\def\autor#1{\gdef\@autor{#1}}
\author{\@autor}

\let\@autora\relax
\def\autora#1{\gdef\@autora{#1}}

\let\@titulo\relax
\def\titulo#1{\gdef\@titulo{#1}}

\def\grau#1{\gdef\@grau{#1}}

\newif\ifmaster

\gdef\mestrado{
  \if\@autora\relax
  \gdef\@degnamept{Mestre}
  \gdef\@degnamees{Maestro}
  \else
  \gdef\@degnamept{Mestra}
  \gdef\@degnamees{Maestra}
  \fi
  \gdef\@degnameen{Master}
  \gdef\@monopt{Disserta\c{c}\~ao}
  \gdef\@monoes{Dissertac\'ion}
  \gdef\@monoen{Dissertation}
}
\gdef\doutorado{
  \if\@autora\relax
  \gdef\@degnamept{Doutor}
  \gdef\@degnamees{Doctor}
  \else
  \gdef\@degnamept{Doutora}
  \gdef\@degnamees{Doctora}
  \fi
  \gdef\@degnameen{Doctor}
  \gdef\@monopt{Tese}
  \gdef\@monoes{Tesis}
  \gdef\@monoen{Thesis}
}

\let\@orientador\relax
\def\orientador#1{\gdef\@orientador{#1}}

\let\@orientadora\relax
\def\orientadora#1{\gdef\@orientadora{#1}}

\gdef\@advisors{1}
\let\@coorientador\relax
\def\coorientador#1{\gdef\@coorientador{#1}\gdef\@advisors{2}}

\let\@coorientadora\relax
\def\coorientadora#1{\gdef\@coorientadora{#1}\gdef\@advisors{2}}

\def\datadadefesa#1#2#3{
  \gdef\@dia{#1}
  \gdef\@mes{#2}
  \gdef\@ano{#3}
}

\let\@fichacatalografica\relax
\def\fichacatalografica#1{\gdef\@fichacatalografica{#1}}

\let\@avalA\relax
\let\@avalB\relax
\let\@avalC\relax
\let\@avalD\relax
\let\@avalE\relax
\let\@avalF\relax
\let\@avalG\relax
\let\@avalH\relax
\let\@instavalA\relax
\let\@instavalB\relax
\let\@instavalC\relax
\let\@instavalD\relax
\let\@instavalE\relax
\let\@instavalF\relax
\let\@instavalG\relax
\let\@instavalH\relax

\def\avaliadorA#1#2{\gdef\@avalA{#1}\gdef\@instavalA{#2}}
\def\avaliadorB#1#2{\gdef\@avalB{#1}\gdef\@instavalB{#2}}
\def\avaliadorC#1#2{\gdef\@avalC{#1}\gdef\@instavalC{#2}}
\def\avaliadorD#1#2{\gdef\@avalD{#1}\gdef\@instavalD{#2}}
\def\avaliadorE#1#2{\gdef\@avalE{#1}\gdef\@instavalE{#2}}
\def\avaliadorF#1#2{\gdef\@avalF{#1}\gdef\@instavalF{#2}}
\def\avaliadorG#1#2{\gdef\@avalG{#1}\gdef\@instavalG{#2}}
\def\avaliadorH#1#2{\gdef\@avalH{#1}\gdef\@instavalH{#2}}

\let\@cotutela\relax
\def\cotutela#1{\gdef\@cotutela{#1}}


\def\paginasiniciais{
  \newlength{\oldparindent}
  \setlength{\oldparindent}{\parindent}
  \setlength\parindent{0pt}
  \thispagestyle{empty}
  \pagestyle{empty}
  \makeatletter
  \let\ps@mystyle\ps@plain
  \let\ps@plain\ps@empty
  \makeatother
  \openningpage
%   \clearpage
%   \titlepage
%   \clearpage
%   \cathpage
%   \clearpage
%   \approvalpage
%   \clearpage
  \setlength{\parindent}{\oldparindent}
  \resetlang
}


\def\logos{
  \noindent
  \begin{center}
  \begin{tabular}{ccc}
    \raisebox{-.5\height}{\includegraphics[width=2.2cm]{logo-unicamp.eps}}
    &
    \begin{minipage}{.6\textwidth}
      \centering
      \textbf{\@UNICAMP} \\
      \textbf{\@IC} \\
    \end{minipage}
    &
    \raisebox{-.45\height}{\scalebox{1.11}{\LogoIcUnicampWithName}}
  \end{tabular}
  \end{center}
}


\def\openningpage{
  \logos
  \vskip 1mm % mexe aqui para descer o text.
  \begin{center}
    
  \end{center}
}



\let\@oldbiblio\thebibliography
\renewcommand{\thebibliography}[1]{\addcontentsline{toc}{chapter}{\bibname}\@oldbiblio{#1}}
