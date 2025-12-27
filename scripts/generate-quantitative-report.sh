#!/bin/bash

# Script to generate HTML report from quantitative test results
# Usage: ./generate-quantitative-report.sh [--rebuild] <output_html> <language> <year> <size> <paranoia> <commit_sha> <reports_dir> [results_file]
# 
# Normal mode: ./generate-quantitative-report.sh <results_file> <output_html> <language> <year> <size> <paranoia> <commit_sha> <reports_dir>
# Rebuild mode: ./generate-quantitative-report.sh --rebuild <output_html> <language> <year> <size> <paranoia> <commit_sha> <reports_dir>

set -euo pipefail

# ============================================================================
# CONFIGURATION
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_FILE="${SCRIPT_DIR}/quantitative-template.html"
TEMP_FILES=()

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

# Cleanup temporary files on exit
cleanup() {
    for f in "${TEMP_FILES[@]:-}"; do
        rm -f "$f" 2>/dev/null || true
    done
}
trap cleanup EXIT

# Create a temporary file and track it for cleanup
make_temp() {
    local tmp
    tmp=$(mktemp)
    TEMP_FILES+=("$tmp")
    echo "$tmp"
}

# Print usage information
usage() {
    cat << EOF
Usage: 
  Normal mode:  $0 <results_file> <output_html> <language> <year> <size> <paranoia> <commit_sha> <reports_dir>
  Rebuild mode: $0 --rebuild <output_html> <language> <year> <size> <paranoia> <commit_sha> <reports_dir>

Arguments:
  results_file   JSON file with test results (normal mode only)
  output_html    Output HTML file path
  language       Test language (e.g., en)
  year           Test year (e.g., 2024)
  size           Test size (e.g., 10k)
  paranoia       Paranoia level (e.g., 4)
  commit_sha     Git commit SHA
  reports_dir    Directory containing JSON reports
EOF
    exit 1
}

# Generate change display for a diff value
get_change_display() {
    local diff=$1
    if [ "$diff" -gt 0 ]; then
        echo "change-increase|▲ +${diff}"
    elif [ "$diff" -lt 0 ]; then
        echo "change-decrease|▼ ${diff}"
    else
        echo "change-same|= 0"
    fi
}

# Extract metrics from a JSON report file
extract_metrics() {
    local report_file="$1"
    
    jq -r '{
        false_positives: .falsePositives,
        fp_pl1: (.falsePositivesPerParanoiaLevel["1"] // 0),
        fp_pl2: (.falsePositivesPerParanoiaLevel["2"] // 0),
        fp_pl3: (.falsePositivesPerParanoiaLevel["3"] // 0),
        fp_pl4: (.falsePositivesPerParanoiaLevel["4"] // 0),
        total_time_seconds: .totalTimeSeconds
    }' "$report_file"
}

# Generate a table row HTML for a given report
generate_table_row() {
    local row_id="$1"
    local filename="$2"
    local date="$3"
    local commit_full="$4"
    local commit_short="$5"
    local total_time_minutes="$6"
    local false_positives="$7"
    local fp_color="$8"
    local fp_display="$9"
    local pl1_color="${10}"
    local pl1_display="${11}"
    local pl2_color="${12}"
    local pl2_display="${13}"
    local pl3_color="${14}"
    local pl3_display="${15}"
    local pl4_color="${16}"
    local pl4_display="${17}"
    local has_previous="${18}"
    local diff_output="${19}"
    
    cat << EOF
            <tr>
                <td>$date</td>
                <td><a href="https://github.com/coreruleset/coreruleset/commit/${commit_full}" target="_blank"><code>${commit_short}</code></a></td>
                <td>${total_time_minutes} min</td>
                <td>${false_positives}</td>
                <td class="${fp_color}">${fp_display}</td>
                <td class="${pl1_color}">${pl1_display}</td>
                <td class="${pl2_color}">${pl2_display}</td>
                <td class="${pl3_color}">${pl3_display}</td>
                <td class="${pl4_color}">${pl4_display}</td>
                <td><a href="javascript:void(0);" id="link-${row_id}" onclick="toggleDetails('${row_id}'); return false;">Show</a></td>
                <td><a href="reports/${filename}" target="_blank">📄</a></td>
            </tr>
            <tr id="details-${row_id}" class="details-row">
                <td colspan="11" class="details-cell">
                    <h3>Diff from Previous Run</h3>
EOF
    
    if [ -z "$diff_output" ]; then
        if [ "$has_previous" = "true" ]; then
            cat << EOF
                    <p><em>No changes from previous run</em></p>
EOF
        else
            cat << EOF
                    <p><em>First run - no previous data</em></p>
EOF
        fi
    else
        cat << EOF
                    <div class="diff-content">${diff_output}</div>
EOF
    fi
    
    cat << EOF
                </td>
            </tr>
EOF
}

# Create HTML file from template with placeholders
create_html_from_template() {
    local output="$1"
    local timestamp="$2"
    local language="$3"
    local year="$4"
    local size="$5"
    local paranoia="$6"
    
    if [ ! -f "$TEMPLATE_FILE" ]; then
        echo "Error: Template file not found at $TEMPLATE_FILE" >&2
        exit 1
    fi
    
    sed -e "s/{{TIMESTAMP}}/${timestamp}/g" \
        -e "s/{{LANGUAGE}}/${language}/g" \
        -e "s/{{YEAR}}/${year}/g" \
        -e "s/{{SIZE}}/${size}/g" \
        -e "s/{{PARANOIA}}/${paranoia}/g" \
        "$TEMPLATE_FILE" > "$output"
}

# Parse change display result into color and display components
parse_change_display() {
    local data="$1"
    local var_prefix="$2"
    eval "${var_prefix}_COLOR=\"\${data%|*}\""
    eval "${var_prefix}_DISPLAY=\"\${data#*|}\""
}

# ============================================================================
# MAIN SCRIPT
# ============================================================================

# Validate minimum arguments
if [ $# -lt 7 ]; then
    usage
fi

REBUILD_MODE=false

# Check for --rebuild flag
if [ "$1" = "--rebuild" ]; then
    REBUILD_MODE=true
    OUTPUT_FILE="$2"
    LANGUAGE="$3"
    YEAR="$4"
    SIZE="$5"
    PARANOIA="$6"
    COMMIT_SHA="$7"
    REPORTS_DIR="$8"
else
    RESULTS_FILE="$1"
    OUTPUT_FILE="$2"
    LANGUAGE="$3"
    YEAR="$4"
    SIZE="$5"
    PARANOIA="$6"
    COMMIT_SHA="$7"
    REPORTS_DIR="$8"
    
    # Validate results file exists in normal mode
    if [ ! -f "$RESULTS_FILE" ]; then
        echo "Error: Results file not found: $RESULTS_FILE" >&2
        exit 1
    fi
fi

if [ "$REBUILD_MODE" = true ]; then
    # REBUILD MODE: Read all reports from directory and regenerate everything
    echo "Rebuild mode: Regenerating report from all reports in $REPORTS_DIR"
    
    # Check if reports directory exists
    if [ ! -d "$REPORTS_DIR" ]; then
        echo "Error: Reports directory not found at $REPORTS_DIR" >&2
        exit 1
    fi
    
    # Get current timestamp
    TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M:%S UTC")
    
    # Create new HTML file from template
    create_html_from_template "$OUTPUT_FILE" "$TIMESTAMP" "$LANGUAGE" "$YEAR" "$SIZE" "$PARANOIA"
    
    # Collect all report files, sorted by date_time (compatible with older bash)
    REPORT_FILES=()
    while IFS= read -r -d '' file; do
        REPORT_FILES+=("$file")
    done < <(find "$REPORTS_DIR" -maxdepth 1 -name "*.json" -type f -print0 | sort -z)
    
    if [ ${#REPORT_FILES[@]} -eq 0 ]; then
        echo "No reports found in $REPORTS_DIR"
        exit 0
    fi
    
    echo "Found ${#REPORT_FILES[@]} reports to process"
    
    # Build JSON array from all reports using jq for proper handling
    JSON_FILE=$(make_temp)
    jq -s -c '.' "${REPORT_FILES[@]}" > "$JSON_FILE"
    
    # Validate JSON
    if ! jq empty "$JSON_FILE" >/dev/null 2>&1; then
        echo "Error: Invalid JSON generated" >&2
        exit 1
    fi
    
    # Update the embedded JSON data in the HTML file
    awk -v jsonfile="$JSON_FILE" '
        /<script id="report-data"/ {
            print $0
            printf "    "
            while ((getline line < jsonfile) > 0) {
                print line
            }
            close(jsonfile)
            in_script=1
            next
        }
        /<\/script>/ && in_script {
            print $0
            in_script=0
            next
        }
        in_script { next }
        { print $0 }
    ' "$OUTPUT_FILE" > "${OUTPUT_FILE}.tmp" && mv "${OUTPUT_FILE}.tmp" "$OUTPUT_FILE"
    
    # Generate table rows for each report
    ROWS_FILE=$(make_temp)
    PREVIOUS_FP=0
    PREVIOUS_PL1=0
    PREVIOUS_PL2=0
    PREVIOUS_PL3=0
    PREVIOUS_PL4=0
    PREVIOUS_REPORT=""
    
    for REPORT_FILE in "${REPORT_FILES[@]}"; do
        FILENAME=$(basename "$REPORT_FILE")
        ROW_ID="${FILENAME%.json}"
        
        # Extract date and commit from filename (format: YYYY-MM-DD_HHMMSS_commit.json)
        DATE=$(echo "$FILENAME" | cut -d'_' -f1)
        COMMIT_FULL=$(echo "$FILENAME" | cut -d'_' -f3 | sed 's/.json$//')
        COMMIT_SHORT="${COMMIT_FULL:0:8}"
        
        # Extract metrics using jq
        METRICS=$(extract_metrics "$REPORT_FILE")
        FALSE_POSITIVES=$(echo "$METRICS" | jq -r '.false_positives')
        FP_PL1=$(echo "$METRICS" | jq -r '.fp_pl1')
        FP_PL2=$(echo "$METRICS" | jq -r '.fp_pl2')
        FP_PL3=$(echo "$METRICS" | jq -r '.fp_pl3')
        FP_PL4=$(echo "$METRICS" | jq -r '.fp_pl4')
        TOTAL_TIME_SECONDS=$(echo "$METRICS" | jq -r '.total_time_seconds')
        TOTAL_TIME_MINUTES=$(printf "%.2f" "$(echo "$TOTAL_TIME_SECONDS / 60" | bc -l)")
        
        # Calculate diffs
        FP_DIFF=$((FALSE_POSITIVES - PREVIOUS_FP))
        PL1_DIFF=$((FP_PL1 - PREVIOUS_PL1))
        PL2_DIFF=$((FP_PL2 - PREVIOUS_PL2))
        PL3_DIFF=$((FP_PL3 - PREVIOUS_PL3))
        PL4_DIFF=$((FP_PL4 - PREVIOUS_PL4))
        
        # Get display strings
        FP_DATA=$(get_change_display $FP_DIFF)
        FP_COLOR="${FP_DATA%|*}"
        FP_DISPLAY="${FP_DATA#*|}"
        
        PL1_DATA=$(get_change_display $PL1_DIFF)
        PL1_COLOR="${PL1_DATA%|*}"
        PL1_DISPLAY="${PL1_DATA#*|}"
        
        PL2_DATA=$(get_change_display $PL2_DIFF)
        PL2_COLOR="${PL2_DATA%|*}"
        PL2_DISPLAY="${PL2_DATA#*|}"
        
        PL3_DATA=$(get_change_display $PL3_DIFF)
        PL3_COLOR="${PL3_DATA%|*}"
        PL3_DISPLAY="${PL3_DATA#*|}"
        
        PL4_DATA=$(get_change_display $PL4_DIFF)
        PL4_COLOR="${PL4_DATA%|*}"
        PL4_DISPLAY="${PL4_DATA#*|}"
        
        # Generate diff if we have a previous report
        DIFF_OUTPUT=""
        HAS_PREVIOUS="false"
        if [ -n "$PREVIOUS_REPORT" ]; then
            HAS_PREVIOUS="true"
            DIFF_OUTPUT=$(diff <(jq . "$PREVIOUS_REPORT") <(jq . "$REPORT_FILE") || true)
        fi
        
        # Generate and write table row
        generate_table_row "$ROW_ID" "$FILENAME" "$DATE" "$COMMIT_FULL" "$COMMIT_SHORT" \
            "$TOTAL_TIME_MINUTES" "$FALSE_POSITIVES" "$FP_COLOR" "$FP_DISPLAY" \
            "$PL1_COLOR" "$PL1_DISPLAY" "$PL2_COLOR" "$PL2_DISPLAY" \
            "$PL3_COLOR" "$PL3_DISPLAY" "$PL4_COLOR" "$PL4_DISPLAY" \
            "$HAS_PREVIOUS" "$DIFF_OUTPUT" >> "$ROWS_FILE"
        
        # Update previous values
        PREVIOUS_FP=$FALSE_POSITIVES
        PREVIOUS_PL1=$FP_PL1
        PREVIOUS_PL2=$FP_PL2
        PREVIOUS_PL3=$FP_PL3
        PREVIOUS_PL4=$FP_PL4
        PREVIOUS_REPORT="$REPORT_FILE"
    done
    
    # Reverse rows so newest appears first
    # Each entry is a pair of <tr> blocks (main row + details row)
    # We need to reverse the order of these pairs while keeping each pair intact
    REVERSED_FILE=$(make_temp)
    awk '
        BEGIN { block = ""; block_count = 0; tr_count = 0 }
        {
            block = block $0 "\n"
            if (/<\/tr>/) tr_count++
            if (tr_count == 2) {
                blocks[++block_count] = block
                block = ""
                tr_count = 0
            }
        }
        END {
            for (i = block_count; i >= 1; i--) {
                printf "%s", blocks[i]
            }
        }
    ' "$ROWS_FILE" > "$REVERSED_FILE"
    mv "$REVERSED_FILE" "$ROWS_FILE"
    
    # Insert all rows into HTML (before </tbody>)
    if sed --version >/dev/null 2>&1; then
        # GNU sed - insert file content before </tbody>
        sed -i "/<\\/tbody>/e cat $ROWS_FILE" "$OUTPUT_FILE"
    else
        # BSD sed (macOS) - use awk instead for reliable insertion
        awk -v rowsfile="$ROWS_FILE" '
            /<\/tbody>/ {
                while ((getline line < rowsfile) > 0) {
                    print line
                }
                close(rowsfile)
            }
            { print }
        ' "$OUTPUT_FILE" > "${OUTPUT_FILE}.tmp" && mv "${OUTPUT_FILE}.tmp" "$OUTPUT_FILE"
    fi
    
    echo "Report regenerated successfully at $OUTPUT_FILE"
    exit 0
fi

# NORMAL MODE: Add single result

# Extract metrics from JSON
TOTAL_TIME_SECONDS=$(jq -r '.totalTimeSeconds' "$RESULTS_FILE")
TOTAL_TIME_MINUTES=$(printf "%.2f" "$(echo "$TOTAL_TIME_SECONDS / 60" | bc -l)")
FALSE_POSITIVES=$(jq -r '.falsePositives' "$RESULTS_FILE")
TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M:%S UTC")
DATE=$(date -u +"%Y-%m-%d")
TIME=$(date -u +"%H%M%S")

# Generate unique report filename based on date, time and commit
REPORT_FILENAME="${DATE}_${TIME}_${COMMIT_SHA:0:8}.json"
REPORT_PATH="${REPORTS_DIR}/${REPORT_FILENAME}"

# Create reports directory if it doesn't exist
mkdir -p "${REPORTS_DIR}"

# Extract FP per paranoia level
FP_PL1=$(jq -r '.falsePositivesPerParanoiaLevel."1" // 0' "$RESULTS_FILE")
FP_PL2=$(jq -r '.falsePositivesPerParanoiaLevel."2" // 0' "$RESULTS_FILE")
FP_PL3=$(jq -r '.falsePositivesPerParanoiaLevel."3" // 0' "$RESULTS_FILE")
FP_PL4=$(jq -r '.falsePositivesPerParanoiaLevel."4" // 0' "$RESULTS_FILE")

# Read previous false positives and report path if file exists
# IMPORTANT: Find previous report BEFORE copying the new one
PREVIOUS_FP=0
PREVIOUS_FP_PL1=0
PREVIOUS_FP_PL2=0
PREVIOUS_FP_PL3=0
PREVIOUS_FP_PL4=0
PREVIOUS_REPORT=""
DIFF_OUTPUT=""

if [ -f "$OUTPUT_FILE" ] && [ -d "$REPORTS_DIR" ]; then
    # Find the most recent report file
    PREVIOUS_REPORT=$(ls -t "$REPORTS_DIR"/*.json 2>/dev/null | head -1)
    
    if [ -n "$PREVIOUS_REPORT" ] && [ -f "$PREVIOUS_REPORT" ]; then
        # Extract previous FP values per PL
        PREVIOUS_FP_PL1=$(jq -r '.falsePositivesPerParanoiaLevel["1"] // 0' "$PREVIOUS_REPORT")
        PREVIOUS_FP_PL2=$(jq -r '.falsePositivesPerParanoiaLevel["2"] // 0' "$PREVIOUS_REPORT")
        PREVIOUS_FP_PL3=$(jq -r '.falsePositivesPerParanoiaLevel["3"] // 0' "$PREVIOUS_REPORT")
        PREVIOUS_FP_PL4=$(jq -r '.falsePositivesPerParanoiaLevel["4"] // 0' "$PREVIOUS_REPORT")
        
        # Extract previous total FP
        PREVIOUS_FP=$(jq -r '.falsePositives' "$PREVIOUS_REPORT")
        
        # Create diff between old and new results
        DIFF_OUTPUT=$(diff <(jq . "$PREVIOUS_REPORT") <(jq . "$RESULTS_FILE") || true)
    fi
fi

# NOW copy the results file to the reports directory (after finding previous)
cp "$RESULTS_FILE" "$REPORT_PATH"

FP_DIFF=$((FALSE_POSITIVES - PREVIOUS_FP))
PL1_DIFF=$((FP_PL1 - PREVIOUS_FP_PL1))
PL2_DIFF=$((FP_PL2 - PREVIOUS_FP_PL2))
PL3_DIFF=$((FP_PL3 - PREVIOUS_FP_PL3))
PL4_DIFF=$((FP_PL4 - PREVIOUS_FP_PL4))

# Get display strings for each metric using helper function
FP_DATA=$(get_change_display $FP_DIFF)
FP_COLOR="${FP_DATA%|*}"
FP_DISPLAY="${FP_DATA#*|}"

PL1_DATA=$(get_change_display $PL1_DIFF)
PL1_COLOR="${PL1_DATA%|*}"
PL1_DISPLAY="${PL1_DATA#*|}"

PL2_DATA=$(get_change_display $PL2_DIFF)
PL2_COLOR="${PL2_DATA%|*}"
PL2_DISPLAY="${PL2_DATA#*|}"

PL3_DATA=$(get_change_display $PL3_DIFF)
PL3_COLOR="${PL3_DATA%|*}"
PL3_DISPLAY="${PL3_DATA#*|}"

PL4_DATA=$(get_change_display $PL4_DIFF)
PL4_COLOR="${PL4_DATA%|*}"
PL4_DISPLAY="${PL4_DATA#*|}"

# Check if HTML file exists
if [ ! -f "$OUTPUT_FILE" ]; then
    # Create new HTML file from template
    create_html_from_template "$OUTPUT_FILE" "$TIMESTAMP" "$LANGUAGE" "$YEAR" "$SIZE" "$PARANOIA"
else
    # File exists, insert new row after tbody tag (cross-platform compatible)
    if sed --version >/dev/null 2>&1; then
        # GNU sed (Linux)
        sed -i '/<tbody>/a <!-- NEW_ROW -->' "$OUTPUT_FILE"
    else
        # BSD sed (macOS)
        sed -i.bak '/<tbody>/a\
<!-- NEW_ROW -->
' "$OUTPUT_FILE" && rm -f "$OUTPUT_FILE.bak"
    fi
fi

# Create unique row ID based on date, time and commit
ROW_ID="${DATE}_${TIME}_${COMMIT_SHA:0:8}"

# Escape diff output for HTML
DIFF_HTML=""
HAS_PREVIOUS="false"
if [ -n "$DIFF_OUTPUT" ]; then
    HAS_PREVIOUS="true"
    DIFF_HTML=$(printf '%s\n' "$DIFF_OUTPUT" | sed 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g; s/"/\&quot;/g')
elif [ -n "$PREVIOUS_REPORT" ]; then
    HAS_PREVIOUS="true"
fi

# Create temporary file for new row
NEW_ROW_FILE=$(make_temp)

{
cat <<EOF
            <tr>
                <td>${DATE}</td>
                <td><a href="https://github.com/coreruleset/coreruleset/commit/${COMMIT_SHA}" target="_blank"><code>${COMMIT_SHA:0:8}</code></a></td>
                <td>${TOTAL_TIME_MINUTES} min</td>
                <td>${FALSE_POSITIVES}</td>
                <td class="${FP_COLOR}">${FP_DISPLAY}</td>
                <td class="${PL1_COLOR}">${PL1_DISPLAY}</td>
                <td class="${PL2_COLOR}">${PL2_DISPLAY}</td>
                <td class="${PL3_COLOR}">${PL3_DISPLAY}</td>
                <td class="${PL4_COLOR}">${PL4_DISPLAY}</td>
                <td><a href="javascript:void(0);" id="link-${ROW_ID}" onclick="toggleDetails('${ROW_ID}'); return false;">Show</a></td>
                <td><a href="reports/${REPORT_FILENAME}" target="_blank">📄</a></td>
            </tr>
            <tr id="details-${ROW_ID}" class="details-row">
                <td colspan="11" class="details-cell">
                    <h3>Diff from Previous Run</h3>
EOF

if [ -n "$DIFF_HTML" ]; then
    printf '                    <div class="diff-content">%s</div>\n' "$DIFF_HTML"
elif [ "$HAS_PREVIOUS" = "true" ]; then
    printf '                    <p><em>No changes from previous run</em></p>\n'
else
    printf '                    <p><em>First run - no previous data</em></p>\n'
fi

cat <<EOF
                </td>
            </tr>
EOF
} > "$NEW_ROW_FILE"

# Update embedded report data
# Extract current report data, add new report, and update
if [ -f "$OUTPUT_FILE" ]; then
    # Extract existing report data - get everything between the script tags
    EXISTING_DATA=$(awk '/<script id="report-data"/ {flag=1; next} /<\/script>/ {flag=0} flag' "$OUTPUT_FILE" | tr -d '\n' | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//')
    
    # Create new report entry with date, time, and data
    NEW_REPORT_ENTRY=$(cat "$REPORT_PATH" | jq -c ". + {date: \"${DATE}\", time: \"${TIME}\", timestamp: \"${DATE} ${TIME:0:2}:${TIME:2:2}\"}")
    
    # If existing data is empty array or empty, replace with new array containing one item
    if [ "$EXISTING_DATA" = "[]" ] || [ -z "$EXISTING_DATA" ]; then
        NEW_DATA="[$NEW_REPORT_ENTRY]"
    else
        # Add new report to existing array - check if it's valid JSON first
        if echo "$EXISTING_DATA" | jq empty 2>/dev/null; then
            NEW_DATA=$(echo "$EXISTING_DATA" | jq -c ". + [$NEW_REPORT_ENTRY]")
        else
            # Invalid JSON, start fresh
            NEW_DATA="[$NEW_REPORT_ENTRY]"
        fi
    fi
    
    # Create a temporary file with the updated JSON
    TMP_FILE=$(mktemp)
    awk -v new_data="    $NEW_DATA" '
        /<script id="report-data"/ {
            print
            print new_data
            in_script=1
            next
        }
        /<\/script>/ && in_script {
            in_script=0
        }
        !in_script
    ' "$OUTPUT_FILE" > "$TMP_FILE"
    mv "$TMP_FILE" "$OUTPUT_FILE"
fi

if [ -f "$OUTPUT_FILE" ] && grep -q "<!-- NEW_ROW -->" "$OUTPUT_FILE"; then
    # Replace placeholder with new row using awk for better compatibility
    awk -v rowfile="$NEW_ROW_FILE" '
        /<!-- NEW_ROW -->/ {
            while ((getline line < rowfile) > 0) {
                print line
            }
            close(rowfile)
            next
        }
        { print }
    ' "$OUTPUT_FILE" > "$OUTPUT_FILE.tmp" && mv "$OUTPUT_FILE.tmp" "$OUTPUT_FILE"
else
    # Append to new file
    cat "$NEW_ROW_FILE" >> "$OUTPUT_FILE"
    cat <<EOF >> "$OUTPUT_FILE"
        </tbody>
    </table>
        </div>
    </div>

    <footer>
        <p>Quantitative Test Report | <a href="https://github.com/coreruleset" target="_blank">CRS GitHub</a> | Generated automatically</p>
    </footer>
</body>
</html>
EOF
fi

echo "Report updated successfully at $OUTPUT_FILE"
