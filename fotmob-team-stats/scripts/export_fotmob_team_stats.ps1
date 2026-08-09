param(
    [Parameter(Mandatory = $true)]
    [string]$Url,

    [Parameter(Mandatory = $true)]
    [string]$OutFile
)

$ErrorActionPreference = "Stop"

function Get-JsonFromUrl {
    param([Parameter(Mandatory = $true)][string]$RequestUrl)

    $headers = @{
        "User-Agent" = "Mozilla/5.0 (compatible; Codex FotMob team stats export)"
        "Accept" = "application/json,text/plain,*/*"
    }
    $response = Invoke-WebRequest -Uri $RequestUrl -UseBasicParsing -Headers $headers
    return $response.Content | ConvertFrom-Json
}

function Convert-Participant {
    param($Participant)

    if ($null -eq $Participant) {
        return $null
    }

    [ordered]@{
        rank = $Participant.rank
        team_id = $Participant.teamId
        name = $Participant.name
        country_code = $Participant.ccode
        value = $Participant.value
        stat = $Participant.stat
        team_colors = $Participant.teamColors
    }
}

function Convert-StatRow {
    param($Row)

    [ordered]@{
        rank = $Row.Rank
        team_id = $Row.TeamId
        team_name = $Row.ParticipantName
        country_code = $Row.ParticipantCountryCode
        stat_value = $Row.StatValue
        sub_stat_value = $Row.SubStatValue
        matches_played = $Row.MatchesPlayed
        minutes_played = $Row.MinutesPlayed
        stat_value_count = $Row.StatValueCount
        team_color = $Row.TeamColor
    }
}

if ($Url -notmatch "/teams/?$") {
    throw "Expected a FotMob team stats URL ending in /teams. Received: $Url"
}

$pageHeaders = @{
    "User-Agent" = "Mozilla/5.0 (compatible; Codex FotMob team stats export)"
    "Accept" = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}
$html = (Invoke-WebRequest -Uri $Url -UseBasicParsing -Headers $pageHeaders).Content
$match = [regex]::Match($html, '<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', [System.Text.RegularExpressions.RegexOptions]::Singleline)
if (-not $match.Success) {
    throw "Could not find __NEXT_DATA__ in FotMob page HTML."
}

$nextData = $match.Groups[1].Value | ConvertFrom-Json
$pageProps = $nextData.props.pageProps
$details = $pageProps.details
$teamStats = @($pageProps.stats.teams)

$result = [ordered]@{
    source = [ordered]@{
        url = $Url
        extracted_at_utc = (Get-Date).ToUniversalTime().ToString("o")
        page = $nextData.page
        build_id = $nextData.buildId
    }
    league = [ordered]@{
        id = $details.id
        name = $details.name
        short_name = $details.shortName
        country = $details.country
        selected_season = $details.selectedSeason
        latest_season = $details.latestSeason
        data_provider = $details.dataProvider
    }
    season_stat_links = $pageProps.stats.seasonStatLinks
    team_statistics = @()
}

$orderOnPage = 0
foreach ($stat in $teamStats) {
    $orderOnPage++

    $topThree = @()
    foreach ($participant in @($stat.topThree)) {
        $topThree += Convert-Participant -Participant $participant
    }

    $statRecord = [ordered]@{
        order_on_page = $orderOnPage
        name = $stat.name
        header = $stat.header
        category = $stat.category
        localized_title_id = $stat.localizedTitleId
        order = $stat.order
        fetch_all_url = $stat.fetchAllUrl
        leader = Convert-Participant -Participant $stat.participant
        top_three_from_page = $topThree
        full_ranking = $null
    }

    if ($stat.fetchAllUrl) {
        $fullData = Get-JsonFromUrl -RequestUrl $stat.fetchAllUrl
        $topLists = @($fullData.TopLists)
        if ($topLists.Count -gt 0) {
            $firstList = $topLists[0]
            $rows = @()
            foreach ($row in @($firstList.StatList)) {
                $rows += Convert-StatRow -Row $row
            }
            $statRecord.full_ranking = [ordered]@{
                stat_name = $firstList.StatName
                title = $firstList.Title
                localized_title_id = $firstList.LocalizedTitleId
                rows = $rows
            }
        } else {
            $statRecord.full_ranking = [ordered]@{ raw = $fullData }
        }

        Start-Sleep -Milliseconds 150
    }

    $result.team_statistics += $statRecord
}

$outPath = [System.IO.Path]::GetFullPath($OutFile)
$outDir = [System.IO.Path]::GetDirectoryName($outPath)
if ($outDir -and -not (Test-Path -LiteralPath $outDir)) {
    New-Item -ItemType Directory -Force -Path $outDir | Out-Null
}

$result | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath $outPath -Encoding UTF8

Write-Output "Output: $outPath"
Write-Output "League: $($result.league.name)"
Write-Output "Season: $($result.league.selected_season)"
Write-Output "Team stat categories: $($result.team_statistics.Count)"
