# Test for å støtte Azure sin implementasjon

Siden Skyporten i sin Azure-integrasjon ikke støtter noe mer granulært enn eksakt string-match, så ønsker vi sammen med Digdir å teste ut om man kan minte tokens spesielt for Azure. 

Da kan man minte tokens spesielt for Azure ved å feks sende inn en ekstra audience som gjør at sub-feltet blir `0192:orgnr-scope`. 

Her er en test hvor vi bruker to audiences i tokenet som sendes til Maskinporten, ett som (på sikt) indikerer for skyporten at tokenet skal mintes for Azure og ett som matcher oppsettet hos Az-tilbyderen.

## Tilbyder

Start med å følge oppsettet i [DigDir-docs for Skyporten for tilbydere](https://docs.digdir.no/docs/Maskinporten/maskinporten_skyporten_azure#for-deg-som-skal-tilby-via-azure). Du trenger ikke endre noen ting i denne delen av guiden. 

## Konsument

Når tilbyder-siden er ferdig satt opp skal du opprette en maskinporten-klient på vanlig måte enten via Samarbeidsportalen eller FO. Når dette er gjort må du fetche access token for klienten. Dette gjøres på helt vanlig måte som beskrevet i guiden på FO, men i resource-feltet på JWT-claimet må du legge inn et array av strenger i stedet for en enkelt streng. En av strengene i arrayet må matche med audience-feltet du satt opp i tilbyderdelen av oppsettet. Når du får access-token kan du benytte det mot Azure som vanlig.
