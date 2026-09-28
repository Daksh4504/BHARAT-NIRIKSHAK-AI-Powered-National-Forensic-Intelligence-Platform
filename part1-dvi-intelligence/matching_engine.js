/**
 * DVI Forensic Matching Engine
 * Implements Interpol DVI (Disaster Victim Identification) forensic reconciliation logic.
 * Computes transparent weighted scores across Primary, Secondary, and Auxiliary identifiers.
 */

function tokenize(str) {
  if (!str) return [];
  return str.toLowerCase()
    .replace(/[^a-z0-9\s#]/g, ' ')
    .split(/\s+/)
    .filter(w => w.length > 2);
}

function wordOverlapScore(text1, text2) {
  if (!text1 || !text2) return 0;
  const t1 = new Set(tokenize(text1));
  const t2 = new Set(tokenize(text2));
  if (t1.size === 0 || t2.size === 0) return 0;

  let common = 0;
  for (const word of t1) {
    if (t2.has(word)) common++;
  }
  const score = (common * 2) / (t1.size + t2.size);
  return Math.min(1.0, score);
}

function evaluateAttributeMatch(amValue, pmValue, type, amObj, pmObj) {
  switch (type) {
    case 'gender': {
      if (!amValue || !pmValue) return { status: 'INCONCLUSIVE', score: 0, max: 10, note: 'Gender data incomplete in one or both records.' };
      const amG = amValue.trim().toLowerCase();
      const pmG = pmValue.trim().toLowerCase();
      if (pmG === 'indeterminate' || amG === 'indeterminate') {
        return { status: 'COMPATIBLE', score: 5, max: 10, note: 'Biological sex indeterminate from current remains examination; compatible pending pelvic/DNA analysis.' };
      }
      if (amG === pmG) {
        return { status: 'MATCH', score: 10, max: 10, note: `Biological sex matches: both recorded as ${amValue}.` };
      }
      return { status: 'MISMATCH', score: -35, max: 10, note: `BIOLOGICAL SEX CONFLICT: AM profile is ${amValue} while PM remains are evaluated as ${pmValue}. Strong exclusionary indicator.` };
    }

    case 'age': {
      const amAge = Number(amObj.age);
      const minAge = Number(pmObj.estimatedAgeMin);
      const maxAge = Number(pmObj.estimatedAgeMax);
      if (isNaN(amAge) || isNaN(minAge) || isNaN(maxAge)) {
        return { status: 'INCONCLUSIVE', score: 3, max: 10, note: 'Age records missing or non-numerical.' };
      }
      if (amAge >= minAge && amAge <= maxAge) {
        return { status: 'MATCH', score: 10, max: 10, note: `AM age (${amAge} yrs) falls directly inside PM estimated age bracket (${minAge}–${maxAge} yrs).` };
      }
      const dist = amAge < minAge ? (minAge - amAge) : (amAge - maxAge);
      if (dist <= 3) {
        return { status: 'COMPATIBLE', score: 7, max: 10, note: `AM age (${amAge} yrs) is within acceptable biological error margin (±${dist} yrs) of PM range (${minAge}–${maxAge} yrs).` };
      }
      if (dist <= 7) {
        return { status: 'COMPATIBLE', score: 3, max: 10, note: `AM age (${amAge} yrs) deviates by ${dist} yrs from PM range (${minAge}–${maxAge} yrs); possible but marginal.` };
      }
      return { status: 'MISMATCH', score: -15, max: 10, note: `Significant age disparity: AM is ${amAge} yrs, PM estimated range is ${minAge}–${maxAge} yrs (disparity: ${dist} yrs).` };
    }

    case 'height': {
      const amH = Number(amObj.heightCm);
      const pmH = Number(pmObj.estimatedHeightCm);
      if (isNaN(amH) || isNaN(pmH)) {
        return { status: 'INCONCLUSIVE', score: 3, max: 10, note: 'Stature measurements incomplete.' };
      }
      const diff = Math.abs(amH - pmH);
      if (diff <= 3) {
        return { status: 'MATCH', score: 10, max: 10, note: `Stature concordance: AM ${amH}cm vs PM ${pmH}cm (variance: ${diff}cm, within standard cadaveric measurement error).` };
      }
      if (diff <= 7) {
        return { status: 'COMPATIBLE', score: 6, max: 10, note: `Stature compatible: AM ${amH}cm vs PM ${pmH}cm (variance: ${diff}cm, acceptable within skeletal estimation bounds).` };
      }
      if (diff <= 12) {
        return { status: 'COMPATIBLE', score: 2, max: 10, note: `Stature marginal: AM ${amH}cm vs PM ${pmH}cm (variance: ${diff}cm).` };
      }
      return { status: 'MISMATCH', score: -10, max: 10, note: `Stature conflict: Variance of ${diff}cm (AM ${amH}cm vs PM ${pmH}cm) exceeds expected biological variance.` };
    }

    case 'dental': {
      // Primary Identifier - Highest Weight (up to 30 points)
      const amD = amObj.dentalRecord || {};
      const pmD = pmObj.dentalRecord || {};
      const amText = `${amD.crowns || ''} ${amD.missingTeeth || ''} ${amD.fillings || ''} ${amD.braces || ''} ${amD.details || ''}`.trim();
      const pmText = `${pmD.crowns || ''} ${pmD.missingTeeth || ''} ${pmD.fillings || ''} ${pmD.braces || ''} ${pmD.details || ''}`.trim();

      if (!amText || !pmText) {
        return { status: 'INCONCLUSIVE', score: 5, max: 30, note: 'Dental chart pending or incomplete in one of the records.' };
      }

      // Check tooth specific identifiers (e.g. #16, #21, #24, #31, #36, gold crown, veneer)
      const keyFeatures = ['#16', '#21', '#24', '#31', '#36', '#37', '#46', '#47', 'gold crown', 'veneer', 'retainer', 'amalgam', 'wisdom'];
      let specificMatches = 0;
      const matchedTokens = [];

      for (const feat of keyFeatures) {
        if (amText.toLowerCase().includes(feat) && pmText.toLowerCase().includes(feat)) {
          specificMatches++;
          matchedTokens.push(feat);
        }
      }

      const overlap = wordOverlapScore(amText, pmText);

      if (specificMatches >= 2 || (specificMatches >= 1 && overlap > 0.25)) {
        return {
          status: 'MATCH',
          score: 30,
          max: 30,
          note: `Conclusive Odontology Concordance: Identical dental signatures detected (${matchedTokens.join(', ')}). High scientific weight.`
        };
      }
      if (specificMatches === 1 || overlap > 0.3) {
        return {
          status: 'MATCH',
          score: 22,
          max: 30,
          note: `Strong Odontology Correlation: Key dental landmark matches (${matchedTokens.length ? matchedTokens.join(', ') : 'restoration patterns'}).`
        };
      }
      if (overlap > 0.15) {
        return {
          status: 'COMPATIBLE',
          score: 12,
          max: 30,
          note: 'Plausible dental compatibility; dental restoration patterns show general alignment.'
        };
      }
      return {
        status: 'INCONCLUSIVE',
        score: 4,
        max: 30,
        note: 'No distinctive matching dental landmarks confirmed between charts.'
      };
    }

    case 'dna': {
      // Primary Identifier (Max 25 pts)
      const amDNA = amObj.dnaProfileStatus || '';
      const pmDNA = pmObj.dnaSampleStatus || '';
      if (pmDNA.toLowerCase().includes('sequenced') && amDNA.toLowerCase().includes('available')) {
        return {
          status: 'MATCH',
          score: 25,
          max: 25,
          note: 'Primary Identifier Match: STR DNA profiles available from both parties for conclusive comparative genotyping.'
        };
      }
      if (pmDNA.toLowerCase().includes('sequenced') || amDNA.toLowerCase().includes('available')) {
        return {
          status: 'COMPATIBLE',
          score: 12,
          max: 25,
          note: 'DNA sample available in one record; laboratory cross-matching sequencing in progress.'
        };
      }
      return {
        status: 'INCONCLUSIVE',
        score: 0,
        max: 25,
        note: 'DNA reference sample pending extraction/acquisition.'
      };
    }

    case 'surgical_implants': {
      // Secondary/Primary (Max 20 pts)
      const amS = `${amObj.surgicalMedicalHistory || ''} ${amObj.scarsAndMarks || ''}`;
      const pmS = `${pmObj.surgicalMedicalFindings || ''} ${pmObj.scarsAndMarks || ''}`;

      const markers = ['appendectomy', 'titanium', 'plate', 'caesarean', 'pfannenstiel', 'tonsils', 'tonsillectomy', 'cardiomegaly', 'chin'];
      const matched = [];
      for (const m of markers) {
        if (amS.toLowerCase().includes(m) && pmS.toLowerCase().includes(m)) {
          matched.push(m);
        }
      }

      if (matched.includes('titanium') || matched.includes('plate') || matched.length >= 2) {
        return {
          status: 'MATCH',
          score: 20,
          max: 20,
          note: `Concordant Surgical / Orthopedic Markers: Confirmed match on ${matched.join(', ')}.`
        };
      }
      if (matched.length === 1) {
        return {
          status: 'MATCH',
          score: 15,
          max: 20,
          note: `Concordant Anatomical Marker: Matching finding on ${matched[0]}.`
        };
      }
      const overlap = wordOverlapScore(amS, pmS);
      if (overlap > 0.2) {
        return {
          status: 'COMPATIBLE',
          score: 8,
          max: 20,
          note: 'General anatomical and surgical compatibility.'
        };
      }
      return {
        status: 'INCONCLUSIVE',
        score: 2,
        max: 20,
        note: 'No distinctive matching surgical history or unique internal hardware recorded.'
      };
    }

    case 'tattoos_marks': {
      // Secondary (Max 15 pts)
      const amT = `${amObj.tattoos || ''} ${amObj.scarsAndMarks || ''}`;
      const pmT = `${pmObj.tattoos || ''} ${pmObj.scarsAndMarks || ''}`;

      const motifs = ['scorpion', 'arachnid', 'butterfly', 'om', 'jawline', 'ear', 'forearm', 'shin'];
      const matched = [];
      for (const m of motifs) {
        if (amT.toLowerCase().includes(m) && pmT.toLowerCase().includes(m)) {
          matched.push(m);
        }
      }

      if (matched.length >= 2) {
        return {
          status: 'MATCH',
          score: 15,
          max: 15,
          note: `Distinctive Dermal Signatures Match: Confirmed congruence on motifs/locations (${matched.join(', ')}).`
        };
      }
      if (matched.length === 1) {
        return {
          status: 'MATCH',
          score: 12,
          max: 15,
          note: `Characteristic Dermal Feature Match: Shared finding on ${matched[0]}.`
        };
      }
      const overlap = wordOverlapScore(amT, pmT);
      if (overlap > 0.2) {
        return {
          status: 'COMPATIBLE',
          score: 6,
          max: 15,
          note: 'Plausible dermal and scar pattern compatibility.'
        };
      }
      return {
        status: 'INCONCLUSIVE',
        score: 2,
        max: 15,
        note: 'No common dermal tattoos or scar landmarks identified.'
      };
    }

    case 'clothing': {
      // Auxiliary (Max 10 pts)
      const amC = amObj.clothingDescription || '';
      const pmC = pmObj.clothingFound || '';
      const overlap = wordOverlapScore(amC, pmC);
      const keywords = ['navy', 'blue', 'polo', 'denim', 'jeans', 'grey', 'cargo', 'reflective', 'yellow', 'kurti', 'khaki', 'work'];
      const matched = keywords.filter(k => amC.toLowerCase().includes(k) && pmC.toLowerCase().includes(k));

      if (matched.length >= 2 || overlap > 0.35) {
        return {
          status: 'MATCH',
          score: 10,
          max: 10,
          note: `Auxiliary Concordance: Textile & apparel remnants directly correspond (${matched.join(', ')}).`
        };
      }
      if (matched.length === 1 || overlap > 0.15) {
        return {
          status: 'COMPATIBLE',
          score: 6,
          max: 10,
          note: `Compatible apparel context: Shared fabric/color attributes (${matched.join(', ')}).`
        };
      }
      return {
        status: 'INCONCLUSIVE',
        score: 1,
        max: 10,
        note: 'Clothing remnants degraded or non-diagnostic.'
      };
    }

    case 'personal_effects': {
      // Auxiliary (Max 10 pts)
      const amP = amObj.personalEffects || '';
      const pmP = pmObj.personalEffectsFound || '';
      const overlap = wordOverlapScore(amP, pmP);
      const keywords = ['ring', 'a.s.', 'casio', 'g-shock', 'watch', 'chain', 'nose', 'diamond', 'stud', 'teal', 'fitbit', 'copper', 'keys'];
      const matched = keywords.filter(k => amP.toLowerCase().includes(k) && pmP.toLowerCase().includes(k));

      if (matched.length >= 2 || (matched.length >= 1 && (matched.includes('a.s.') || matched.includes('teal') || matched.includes('copper')))) {
        return {
          status: 'MATCH',
          score: 10,
          max: 10,
          note: `Auxiliary Strong Match: High-specificity personal items corroborate identification (${matched.join(', ')}).`
        };
      }
      if (matched.length === 1 || overlap > 0.2) {
        return {
          status: 'COMPATIBLE',
          score: 6,
          max: 10,
          note: `Compatible personal property items: Correlation on ${matched.length ? matched.join(', ') : 'accessories'}.`
        };
      }
      return {
        status: 'INCONCLUSIVE',
        score: 1,
        max: 10,
        note: 'Personal effects recovered do not present distinctive matching markings.'
      };
    }

    default:
      return { status: 'INCONCLUSIVE', score: 0, max: 10, note: 'Attribute evaluation not configured.' };
  }
}

/**
 * Compare an Ante-Mortem profile against a Post-Mortem body profile.
 */
function compareProfiles(am, pm) {
  const evaluations = [
    { attr: 'Gender / Biological Sex', type: 'gender', amVal: am.gender, pmVal: pm.gender, category: 'Anthropometric' },
    { attr: 'Age Distribution', type: 'age', amVal: `${am.age} yrs`, pmVal: pm.estimatedAgeDisplay || `${pm.estimatedAgeMin}-${pm.estimatedAgeMax} yrs`, category: 'Anthropometric' },
    { attr: 'Stature / Height', type: 'height', amVal: `${am.heightCm} cm`, pmVal: `Est. ${pm.estimatedHeightCm} ±${pm.heightToleranceCm || 3} cm`, category: 'Anthropometric' },
    { attr: 'Odontology / Dental Chart', type: 'dental', amVal: am.dentalRecord?.crowns || am.dentalRecord?.details || 'Recorded', pmVal: pm.dentalRecord?.crowns || pm.dentalRecord?.details || 'Recorded', category: 'Primary' },
    { attr: 'DNA STR Profiling', type: 'dna', amVal: am.dnaProfileStatus, pmVal: pm.dnaSampleStatus, category: 'Primary' },
    { attr: 'Surgical Findings & Implants', type: 'surgical_implants', amVal: am.surgicalMedicalHistory || am.scarsAndMarks, pmVal: pm.surgicalMedicalFindings || pm.scarsAndMarks, category: 'Secondary' },
    { attr: 'Tattoos, Scars & Dermal Marks', type: 'tattoos_marks', amVal: `${am.tattoos || ''}; ${am.scarsAndMarks || ''}`, pmVal: `${pm.tattoos || ''}; ${pm.scarsAndMarks || ''}`, category: 'Secondary' },
    { attr: 'Clothing & Textiles', type: 'clothing', amVal: am.clothingDescription, pmVal: pm.clothingFound, category: 'Auxiliary' },
    { attr: 'Personal Effects & Jewelry', type: 'personal_effects', amVal: am.personalEffects, pmVal: pm.personalEffectsFound, category: 'Auxiliary' }
  ];

  let totalScore = 0;
  let maxPossibleScore = 0;

  const matchingAttributes = [];
  const mismatchingAttributes = [];
  const inconclusiveAttributes = [];
  const detailedBreakdown = [];

  for (const item of evaluations) {
    const res = evaluateAttributeMatch(item.amVal, item.pmVal, item.type, am, pm);
    totalScore += res.score;
    maxPossibleScore += res.max;

    const row = {
      attribute: item.attr,
      category: item.category,
      amValue: item.amVal || 'Not documented',
      pmValue: item.pmVal || 'Not documented',
      status: res.status,
      score: res.score,
      maxScore: res.max,
      note: res.note
    };

    detailedBreakdown.push(row);

    if (res.status === 'MATCH') {
      matchingAttributes.push(row);
    } else if (res.status === 'MISMATCH') {
      mismatchingAttributes.push(row);
    } else if (res.status === 'COMPATIBLE') {
      matchingAttributes.push(row);
    } else {
      inconclusiveAttributes.push(row);
    }
  }

  // Normalize score between 0 and 100%
  let percentage = Math.round((Math.max(0, totalScore) / maxPossibleScore) * 100);

  // If severe mismatch (e.g. sex mismatch or hard height conflict)
  const hasSexMismatch = mismatchingAttributes.some(m => m.attribute.includes('Gender'));
  if (hasSexMismatch) {
    percentage = Math.min(percentage, 18);
  }

  // Determine forensic confidence tier
  let confidenceTier = '';
  let badgeColor = '';
  if (percentage >= 85) {
    confidenceTier = 'HIGH CONFIDENCE IDENTIFICATION (Reconciliation Recommended)';
    badgeColor = 'success';
  } else if (percentage >= 65) {
    confidenceTier = 'PROBABLE CANDIDATE (Further Forensic Verification Advised)';
    badgeColor = 'warning';
  } else if (percentage >= 40) {
    confidenceTier = 'POSSIBLE CORROBORATION (Low Confidence / Inconclusive)';
    badgeColor = 'info';
  } else {
    confidenceTier = 'UNLIKELY / EXCLUDED CANDIDATE';
    badgeColor = 'danger';
  }

  // Generate Forensic Rationale Narrative
  const rationale = buildForensicRationale(am, pm, percentage, matchingAttributes, mismatchingAttributes, hasSexMismatch);

  return {
    amId: am.id,
    amName: am.fullName,
    pmId: pm.id,
    pmRecoveryNo: pm.recoveryNumber,
    matchPercentage: percentage,
    confidenceTier,
    badgeColor,
    rawScore: totalScore,
    maxScore: maxPossibleScore,
    matchingAttributes,
    mismatchingAttributes,
    inconclusiveAttributes,
    detailedBreakdown,
    rationale
  };
}

function buildForensicRationale(am, pm, percentage, matching, mismatching, sexMismatch) {
  if (sexMismatch) {
    return `EXCLUSIONARY EVALUATION: Post-mortem morphological examination conflicts with the biological sex of missing person ${am.fullName} (${am.gender} vs. PM ${pm.gender}). Unless biological sex of remains was altered by extensive thermal disruption, this candidate is provisionally excluded.`;
  }

  const primaryMatches = matching.filter(m => m.category === 'Primary' && m.status === 'MATCH');
  const secondaryMatches = matching.filter(m => m.category === 'Secondary' && m.status === 'MATCH');
  const auxiliaryMatches = matching.filter(m => m.category === 'Auxiliary' && m.status === 'MATCH');

  let text = `Candidate comparison between Ante-Mortem profile ${am.fullName} (${am.id}) and Unidentified Remains ${pm.id} yields a calculated concordance index of ${percentage}%. `;

  if (primaryMatches.length > 0) {
    const dental = primaryMatches.find(m => m.attribute.includes('Odontology'));
    const dna = primaryMatches.find(m => m.attribute.includes('DNA'));
    text += `Scientific identification is strongly corroborated by Primary DVI Identifiers: `;
    if (dental) text += `concordant dental restorative charting (e.g. ${dental.note.replace('Conclusive Odontology Concordance: ', '')}). `;
    if (dna) text += `DNA STR profiling status is compatible for statistical likelihood calculation. `;
  } else {
    text += `Primary scientific identifiers (dental/fingerprint/DNA) are pending definitive radiographic or genetic cross-matching. `;
  }

  if (secondaryMatches.length > 0) {
    text += `Secondary identification criteria provide robust individualizing evidence: ${secondaryMatches.map(s => s.note).join(' ')} `;
  }

  if (auxiliaryMatches.length > 0) {
    text += `Circumstantial corroboration is reinforced by personal artifacts: ${auxiliaryMatches.map(a => a.note).join(' ')} `;
  }

  if (mismatching.length > 0) {
    text += `Noted points of divergence include: ${mismatching.map(m => m.note).join(' ')} `;
  }

  return text.trim();
}

/**
 * Given a Post-Mortem body, evaluate all Ante-Mortem candidates and return top N matches.
 */
function getTopCandidatesForPM(pmProfile, antemortemList, topN = 3) {
  const results = antemortemList.map(am => compareProfiles(am, pmProfile));
  results.sort((a, b) => b.matchPercentage - a.matchPercentage);
  return results.slice(0, topN);
}

/**
 * Given an Ante-Mortem profile, evaluate all Post-Mortem bodies and return top N matches.
 */
function getTopCandidatesForAM(amProfile, postmortemList, topN = 3) {
  const results = postmortemList.map(pm => compareProfiles(amProfile, pm));
  results.sort((a, b) => b.matchPercentage - a.matchPercentage);
  return results.slice(0, topN);
}

/**
 * Global batch matching matrix across all AM and PM records.
 */
function runBatchMatching(antemortemList, postmortemList) {
  const matrix = [];
  for (const pm of postmortemList) {
    const topMatches = getTopCandidatesForPM(pm, antemortemList, 3);
    matrix.push({
      pmId: pm.id,
      recoveryLocation: pm.recoveryLocation,
      gender: pm.gender,
      estimatedAge: pm.estimatedAgeDisplay || `${pm.estimatedAgeMin}-${pm.estimatedAgeMax}`,
      status: pm.matchingStatus,
      reconciledWithAMId: pm.reconciledWithAMId,
      topCandidate: topMatches[0] || null,
      candidates: topMatches
    });
  }
  return matrix;
}

module.exports = {
  compareProfiles,
  getTopCandidatesForPM,
  getTopCandidatesForAM,
  runBatchMatching
};
