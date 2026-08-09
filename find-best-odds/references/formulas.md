# Formula Templates

These formulas are written for Google Sheets files using Danish locale separators: semicolon argument separators and comma decimal formatting.

Each formula assumes:

- bookmaker JSON is in `$G2`
- home team is in `$E2`
- away team is in `$F2`
- formulas are placed in row 2 and copied down

## L: best_odds_1

```text
=IF($G2="";"";IF(MAX(MAP(SPLIT($G2;""",""title"":""";FALSE);LAMBDA(b;IFERROR(VALUE(SUBSTITUTE(REGEXEXTRACT(b;"""name"":"""&$E2&""",""price"":([0-9.]+)");".";","));0))))=0;"";MAX(MAP(SPLIT($G2;""",""title"":""";FALSE);LAMBDA(b;IFERROR(VALUE(SUBSTITUTE(REGEXEXTRACT(b;"""name"":"""&$E2&""",""price"":([0-9.]+)");".";","));0))))))
```

## M: bookmaker_1

```text
=IF($L2="";"";INDEX(FILTER(MAP(SPLIT($G2;""",""title"":""";FALSE);LAMBDA(b;IFERROR(REGEXEXTRACT(b;"^([^""]+)");"")));MAP(SPLIT($G2;""",""title"":""";FALSE);LAMBDA(b;IFERROR(VALUE(SUBSTITUTE(REGEXEXTRACT(b;"""name"":"""&$E2&""",""price"":([0-9.]+)");".";","));0)))=$L2);1))
```

## N: best_odds_X

```text
=IF($G2="";"";IF(MAX(MAP(SPLIT($G2;""",""title"":""";FALSE);LAMBDA(b;IFERROR(VALUE(SUBSTITUTE(REGEXEXTRACT(b;"""name"":""Draw"",""price"":([0-9.]+)");".";","));0))))=0;"";MAX(MAP(SPLIT($G2;""",""title"":""";FALSE);LAMBDA(b;IFERROR(VALUE(SUBSTITUTE(REGEXEXTRACT(b;"""name"":""Draw"",""price"":([0-9.]+)");".";","));0))))))
```

## O: bookmaker_X

```text
=IF($N2="";"";INDEX(FILTER(MAP(SPLIT($G2;""",""title"":""";FALSE);LAMBDA(b;IFERROR(REGEXEXTRACT(b;"^([^""]+)");"")));MAP(SPLIT($G2;""",""title"":""";FALSE);LAMBDA(b;IFERROR(VALUE(SUBSTITUTE(REGEXEXTRACT(b;"""name"":""Draw"",""price"":([0-9.]+)");".";","));0)))=$N2);1))
```

## P: best_odds_2

```text
=IF($G2="";"";IF(MAX(MAP(SPLIT($G2;""",""title"":""";FALSE);LAMBDA(b;IFERROR(VALUE(SUBSTITUTE(REGEXEXTRACT(b;"""name"":"""&$F2&""",""price"":([0-9.]+)");".";","));0))))=0;"";MAX(MAP(SPLIT($G2;""",""title"":""";FALSE);LAMBDA(b;IFERROR(VALUE(SUBSTITUTE(REGEXEXTRACT(b;"""name"":"""&$F2&""",""price"":([0-9.]+)");".";","));0))))))
```

## Q: bookmaker_2

```text
=IF($P2="";"";INDEX(FILTER(MAP(SPLIT($G2;""",""title"":""";FALSE);LAMBDA(b;IFERROR(REGEXEXTRACT(b;"^([^""]+)");"")));MAP(SPLIT($G2;""",""title"":""";FALSE);LAMBDA(b;IFERROR(VALUE(SUBSTITUTE(REGEXEXTRACT(b;"""name"":"""&$F2&""",""price"":([0-9.]+)");".";","));0)))=$P2);1))
```

## R: odds_found

```text
=AND($L2<>"";$N2<>"";$P2<>"")
```
