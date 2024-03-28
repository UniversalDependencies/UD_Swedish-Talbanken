## TODO
### Things to do:
    "svart"-form -> No Gender, Number 
    bra -> No Gender, No Number, No Definite

    

### Things to enforce:
    Adj med endast en form (bra, udda) -> Bara Degree=Pos, Case=Nom
    lemman som slutar på t men borde sluta på d -> ont, runt, osv.


### Decisions to make:
    Abbr -> Degree=Pos, Case=Nom, Lemma=oförkortad
    o+particip (okokt, ogift)
    prefix utan partikelverb+particip (nygift)

    Should superlative 'ste' have Definite since it can occur with either and you cannot neccessarily tell from the form?

    Inre, yttre, övre
    tredje - vad är lemma
    
    


## Done

### Fixed expressions
    Extract from PUD
    Update Lars' spreadsheet

### Features
    Kolla om Nom, Pos, Plur -> Ind
    Definite=Def -> no Number (if not ending with e or es, such as svarte/svartes)
    Remove -> gender=Masc


# Mötesanteckningen
## Lemman:
### Particip – hur många typer och principer för lemman?
    alla particip ska ha participform som lemma
    utrum-sing, partikel sitter kvar.
    se till att de inte har verb som lemma och att lemmat inte är böjt.



### Partikelverb – specialfall som också påverkar lemman för VERB
    testa om ADJ med VOICE=PASS eller NSUBJ:PASS hur det påverkar 
    bortförd - bortförd - VERB -> ADJ?
    bortförd - bortförd - ADJ
    föra bort - föra - VERB
    bortföra - bortföre - VERB


### Ordningstal (“tre” eller “tredje”)
    tredje


### Övrigt (bl.a. förkortningar och komparativ/superlativ utan positiv typ “inre”)
    förkortningar ska ha oförkortade, flerordsuttryck inte bestämd 

    övre - övre
    översta - övre

    södra - södra (def)

## Särdrag:
### Kombinationer av Definite och Number (troligen redan klart)
    a-form:
        Def - Ingen Number
        Ind - Plur

    
        
### Underspecificerade former (typen “svart” och “bra”)
    läxa kommentera filerna

### Överspecificerade former (t.ex. “lilla”)


### Definite på superlativer
    om slutar på st så är det obestämd (i predikativ ställning)


### Particip – följer av lemmadiskussionen?
    tempus - skiljer past och pres
    om de är participliknande men inte är tillräckligt kopplade till ett verb ska de inte ha participtagg?
    ska finnas i ett verbparadigm, inte en ersättare

## Determinerare
### ska nästa/sista vara determinerare eller ADJ?
    ta fram alla former ordklass DET och syntaktisk funktion DET och se om det finns något som inte ska finnas
    för varje form, ta fram alla variation av taggar (ordklasser) och syntaktisk funktion
    finns det  som finns ord som klassas både som DET och som ADJ.












