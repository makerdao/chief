// DssChief.spec

using TokenMock as gov;
using Auxiliar as aux;

methods {
    function live() external returns (uint256) envfree;
    function hat() external returns (address) envfree;
    function slates(bytes32, uint256) external returns (address) envfree;
    function votes(address) external returns (bytes32) envfree;
    function approvals(address) external returns (uint256) envfree;
    function deposits(address) external returns (uint256) envfree;
    function last(address) external returns (uint256) envfree;
    function gov() external returns (address) envfree;
    function maxYays() external returns (uint256) envfree;
    function launchThreshold() external returns (uint256) envfree;
    function length(bytes32) external returns (uint256) envfree;
    function gov.allowance(address, address) external returns (uint256) envfree;
    function gov.balanceOf(address) external returns (uint256) envfree;
    function aux.hashYays(address[]) external returns (bytes32) envfree;
}

// Verify correct storage changes for non reverting launch
rule launch() {
    env e;

    bytes32 anyB32;
    uint256 anyUint;
    address anyAddr;

    address hatBefore = hat();
    address slatesBefore = slates(anyB32, anyUint);
    bytes32 votesBefore = votes(anyAddr);
    mathint approvalsBefore = approvals(anyAddr);
    mathint depositsBefore = deposits(anyAddr);
    mathint lastBefore = last(anyAddr);

    launch(e);

    mathint liveAfter = live();
    address hatAfter = hat();
    address slatesAfter = slates(anyB32, anyUint);
    bytes32 votesAfter = votes(anyAddr);
    mathint approvalsAfter = approvals(anyAddr);
    mathint depositsAfter = deposits(anyAddr);
    mathint lastAfter = last(anyAddr);

    assert liveAfter == 1, "launch did not set live to 1";
    assert hatAfter == hatBefore, "launch did not keep unchanged hat";
    assert slatesAfter == slatesBefore, "launch did not keep unchanged every slates[x][y]";
    assert votesAfter == votesBefore, "launch did not keep unchanged every votes[x]";
    assert approvalsAfter == approvalsBefore, "launch did not keep unchanged every approvals[x]";
    assert depositsAfter == depositsBefore, "launch did not keep unchanged every deposits[x]";
    assert lastAfter == lastBefore, "launch did not keep unchanged every last[x]";
}

// Verify revert rules on launch
rule launch_revert() {
    env e;

    mathint live = live();
    address hat = hat();
    address addr0 = 0;
    mathint approvalsAddr0 = approvals(addr0);
    mathint launchThreshold = launchThreshold();

    launch@withrevert(e);

    bool revert1 = e.msg.value > 0;
    bool revert2 = live != 0;
    bool revert3 = hat != addr0;
    bool revert4 = approvalsAddr0 < launchThreshold;

    assert revert1 => lastReverted, "revert1 failed";
    assert revert2 => lastReverted, "revert2 failed";
    assert revert3 => lastReverted, "revert3 failed";
    assert revert4 => lastReverted, "revert4 failed";
    assert lastReverted => revert1 || revert2 || revert3 ||
                           revert4, "Revert rules are not covering all the cases";
}

// Verify correct storage changes for non reverting lock
rule lock(uint256 wad) {
    env e;

    require e.msg.sender != currentContract;

    mathint maxYays = maxYays();
    require maxYays == 5;

    bytes32 anyB32;
    uint256 anyUint;
    address anyAddr;

    address otherAddr;
    require otherAddr != e.msg.sender;

    address otherAddr2;
    require otherAddr2 != e.msg.sender && otherAddr2 != currentContract;

    mathint liveBefore = live();
    address hatBefore = hat();
    address slatesBefore = slates(anyB32, anyUint);
    bytes32 votesBefore = votes(anyAddr);
    bytes32 votesSender = votes(e.msg.sender);
    mathint lengthVotesSender = length(votesSender);
    require lengthVotesSender <= maxYays;
    address addr0 = 0;
    address slatesVotesSender0 = lengthVotesSender >= 1 ? slates(votesSender, 0) : addr0; // Just any address as placeholder
    address slatesVotesSender1 = lengthVotesSender >= 2 ? slates(votesSender, 1) : addr0;
    address slatesVotesSender2 = lengthVotesSender >= 3 ? slates(votesSender, 2) : addr0;
    address slatesVotesSender3 = lengthVotesSender >= 4 ? slates(votesSender, 3) : addr0;
    address slatesVotesSender4 = lengthVotesSender == 5 ? slates(votesSender, 4) : addr0;
    require lengthVotesSender <= 1 || slatesVotesSender1 > slatesVotesSender0;
    require lengthVotesSender <= 2 || slatesVotesSender2 > slatesVotesSender1;
    require lengthVotesSender <= 3 || slatesVotesSender3 > slatesVotesSender2;
    require lengthVotesSender <= 4 || slatesVotesSender4 > slatesVotesSender3;
    address slatessNotSenderAny;
    require (lengthVotesSender < 1 || slatessNotSenderAny != slatesVotesSender0) &&
            (lengthVotesSender < 2 || slatessNotSenderAny != slatesVotesSender1) &&
            (lengthVotesSender < 3 || slatessNotSenderAny != slatesVotesSender2) &&
            (lengthVotesSender < 4 || slatessNotSenderAny != slatesVotesSender3) &&
            (lengthVotesSender < 5 || slatessNotSenderAny != slatesVotesSender4);
    mathint approvalsSlatesSender0Before = approvals(slatesVotesSender0);
    mathint approvalsSlatesSender1Before = approvals(slatesVotesSender1);
    mathint approvalsSlatesSender2Before = approvals(slatesVotesSender2);
    mathint approvalsSlatesSender3Before = approvals(slatesVotesSender3);
    mathint approvalsSlatesSender4Before = approvals(slatesVotesSender4);
    mathint approvalsSlatesNotSenderAnyBefore = approvals(slatessNotSenderAny);
    mathint depositsSenderBefore = deposits(e.msg.sender);
    mathint depositsOtherBefore = deposits(otherAddr);
    mathint lastOtherBefore = last(otherAddr);
    mathint govBalanceOfSenderBefore = gov.balanceOf(e.msg.sender);
    mathint govBalanceOfChiefBefore = gov.balanceOf(currentContract);
    mathint govBalanceOfOtherBefore = gov.balanceOf(otherAddr2);

    lock(e, wad);

    mathint liveAfter = live();
    address hatAfter = hat();
    address slatesAfter = slates(anyB32, anyUint);
    bytes32 votesAfter = votes(anyAddr);
    mathint approvalsSlatesSender0After = approvals(slatesVotesSender0);
    mathint approvalsSlatesSender1After = approvals(slatesVotesSender1);
    mathint approvalsSlatesSender2After = approvals(slatesVotesSender2);
    mathint approvalsSlatesSender3After = approvals(slatesVotesSender3);
    mathint approvalsSlatesSender4After = approvals(slatesVotesSender4);
    mathint approvalsSlatesNotSenderAnyAfter = approvals(slatessNotSenderAny);
    mathint depositsSenderAfter = deposits(e.msg.sender);
    mathint depositsOtherAfter = deposits(otherAddr);
    mathint lastSenderAfter = last(e.msg.sender);
    mathint lastOtherAfter = last(otherAddr);
    mathint govBalanceOfSenderAfter = gov.balanceOf(e.msg.sender);
    mathint govBalanceOfChiefAfter = gov.balanceOf(currentContract);
    mathint govBalanceOfOtherAfter = gov.balanceOf(otherAddr2);

    assert liveAfter == liveBefore, "lock did not keep unchanged live";
    assert hatAfter == hatBefore, "lock did not keep unchanged hat";
    assert slatesAfter == slatesBefore, "lock did not keep unchanged every slates[x][y]";
    assert votesAfter == votesBefore, "lock did not keep unchanged every votes[x]";
    assert lengthVotesSender >= 1 => approvalsSlatesSender0After == approvalsSlatesSender0Before + wad, "lock did not increase approvals[slatesVotesSender0] by wad";
    assert lengthVotesSender >= 2 => approvalsSlatesSender1After == approvalsSlatesSender1Before + wad, "lock did not increase approvals[slatesVotesSender1] by wad";
    assert lengthVotesSender >= 3 => approvalsSlatesSender2After == approvalsSlatesSender2Before + wad, "lock did not increase approvals[slatesVotesSender2] by wad";
    assert lengthVotesSender >= 4 => approvalsSlatesSender3After == approvalsSlatesSender3Before + wad, "lock did not increase approvals[slatesVotesSender3] by wad";
    assert lengthVotesSender == 5 => approvalsSlatesSender4After == approvalsSlatesSender4Before + wad, "lock did not increase approvals[slatesVotesSender4] by wad";
    assert approvalsSlatesNotSenderAnyAfter == approvalsSlatesNotSenderAnyBefore, "lock did not keep unchanged the rest of approvals[x]";
    assert depositsSenderAfter == depositsSenderBefore + wad, "lock did not increase deposits[sender] by wad";
    assert depositsOtherAfter == depositsOtherBefore, "lock did not keep unchanged the rest of deposits[x]";
    assert lastSenderAfter == to_mathint(e.block.number), "lock did not set last[sender] to block.number";
    assert lastOtherAfter == lastOtherBefore, "lock did not keep unchanged the rest of last[x]";
    assert govBalanceOfSenderAfter == govBalanceOfSenderBefore - wad, "lock did not decrease gov.balanceOf[sender] by wad";
    assert govBalanceOfChiefAfter == govBalanceOfChiefBefore + wad, "lock did not increase gov.balanceOf[chief] by wad";
    assert govBalanceOfOtherAfter == govBalanceOfOtherBefore, "lock did not keep unchanged the rest of gov.balanceOf[x]";
}

// Verify revert rules on lock
rule lock_revert(uint256 wad) {
    env e;

    mathint maxYays = maxYays();
    require maxYays == 5;
    require gov.balanceOf(e.msg.sender) >= wad;
    require gov.allowance(e.msg.sender, currentContract) >= wad;

    mathint depositsSender = deposits(e.msg.sender);
    bytes32 votesSender = votes(e.msg.sender);
    mathint lengthVotesSender = length(votesSender);
    require lengthVotesSender <= maxYays;
    address addr0 = 0;
    address slatesVotesSender0 = lengthVotesSender >= 1 ? slates(votesSender, 0) : addr0; // Just any address as placeholder
    address slatesVotesSender1 = lengthVotesSender >= 2 ? slates(votesSender, 1) : addr0;
    address slatesVotesSender2 = lengthVotesSender >= 3 ? slates(votesSender, 2) : addr0;
    address slatesVotesSender3 = lengthVotesSender >= 4 ? slates(votesSender, 3) : addr0;
    address slatesVotesSender4 = lengthVotesSender == 5 ? slates(votesSender, 4) : addr0;
    require lengthVotesSender <= 1 || slatesVotesSender1 > slatesVotesSender0;
    require lengthVotesSender <= 2 || slatesVotesSender2 > slatesVotesSender1;
    require lengthVotesSender <= 3 || slatesVotesSender3 > slatesVotesSender2;
    require lengthVotesSender <= 4 || slatesVotesSender4 > slatesVotesSender3;
    mathint approvalsSlatesVotesSender0 = approvals(slatesVotesSender0);
    mathint approvalsSlatesVotesSender1 = approvals(slatesVotesSender1);
    mathint approvalsSlatesVotesSender2 = approvals(slatesVotesSender2);
    mathint approvalsSlatesVotesSender3 = approvals(slatesVotesSender3);
    mathint approvalsSlatesVotesSender4 = approvals(slatesVotesSender4);

    lock@withrevert(e, wad);

    bool revert1 = e.msg.value > 0;
    bool revert2 = depositsSender + wad > max_uint256;
    bool revert3 = lengthVotesSender >= 1 && approvalsSlatesVotesSender0 + wad > max_uint256;
    bool revert4 = lengthVotesSender >= 2 && approvalsSlatesVotesSender1 + wad > max_uint256;
    bool revert5 = lengthVotesSender >= 3 && approvalsSlatesVotesSender2 + wad > max_uint256;
    bool revert6 = lengthVotesSender >= 4 && approvalsSlatesVotesSender3 + wad > max_uint256;
    bool revert7 = lengthVotesSender == 5 && approvalsSlatesVotesSender4 + wad > max_uint256;

    assert revert1 => lastReverted, "revert1 failed";
    assert revert2 => lastReverted, "revert2 failed";
    assert revert3 => lastReverted, "revert3 failed";
    assert revert4 => lastReverted, "revert4 failed";
    assert revert5 => lastReverted, "revert5 failed";
    assert revert6 => lastReverted, "revert6 failed";
    assert revert7 => lastReverted, "revert7 failed";
    assert lastReverted => revert1 || revert2 || revert3 ||
                           revert4 || revert5 || revert6 ||
                           revert7, "Revert rules are not covering all the cases";
}

// Verify correct storage changes for non reverting free
rule free(uint256 wad) {
    env e;

    require e.msg.sender != currentContract;

    mathint maxYays = maxYays();
    require maxYays == 5;

    bytes32 anyB32;
    uint256 anyUint;
    address anyAddr;

    address otherAddr;
    require otherAddr != e.msg.sender;

    address otherAddr2;
    require otherAddr2 != e.msg.sender && otherAddr2 != currentContract;

    mathint liveBefore = live();
    address hatBefore = hat();
    address slatesBefore = slates(anyB32, anyUint);
    bytes32 votesBefore = votes(anyAddr);
    bytes32 votesSender = votes(e.msg.sender);
    mathint lengthVotesSender = length(votesSender);
    require lengthVotesSender <= maxYays;
    address addr0 = 0;
    address slatesVotesSender0 = lengthVotesSender >= 1 ? slates(votesSender, 0) : addr0; // Just any address as placeholder
    address slatesVotesSender1 = lengthVotesSender >= 2 ? slates(votesSender, 1) : addr0;
    address slatesVotesSender2 = lengthVotesSender >= 3 ? slates(votesSender, 2) : addr0;
    address slatesVotesSender3 = lengthVotesSender >= 4 ? slates(votesSender, 3) : addr0;
    address slatesVotesSender4 = lengthVotesSender == 5 ? slates(votesSender, 4) : addr0;
    require lengthVotesSender <= 1 || slatesVotesSender1 > slatesVotesSender0;
    require lengthVotesSender <= 2 || slatesVotesSender2 > slatesVotesSender1;
    require lengthVotesSender <= 3 || slatesVotesSender3 > slatesVotesSender2;
    require lengthVotesSender <= 4 || slatesVotesSender4 > slatesVotesSender3;
    address slatesNotSenderAny;
    require (lengthVotesSender < 1 || slatesNotSenderAny != slatesVotesSender0) &&
            (lengthVotesSender < 2 || slatesNotSenderAny != slatesVotesSender1) &&
            (lengthVotesSender < 3 || slatesNotSenderAny != slatesVotesSender2) &&
            (lengthVotesSender < 4 || slatesNotSenderAny != slatesVotesSender3) &&
            (lengthVotesSender < 5 || slatesNotSenderAny != slatesVotesSender4);
    mathint approvalsSlatesVotesSender0Before = approvals(slatesVotesSender0);
    mathint approvalsSlatesVotesSender1Before = approvals(slatesVotesSender1);
    mathint approvalsSlatesVotesSender2Before = approvals(slatesVotesSender2);
    mathint approvalsSlatesVotesSender3Before = approvals(slatesVotesSender3);
    mathint approvalsSlatesVotesSender4Before = approvals(slatesVotesSender4);
    mathint approvalsSlatesVotesNotSenderAnyBefore = approvals(slatesNotSenderAny);
    mathint depositsSenderBefore = deposits(e.msg.sender);
    mathint depositsOtherBefore = deposits(otherAddr);
    mathint lastBefore = last(anyAddr);
    mathint govBalanceOfSenderBefore = gov.balanceOf(e.msg.sender);
    mathint govBalanceOfChiefBefore = gov.balanceOf(currentContract);
    mathint govBalanceOfOtherBefore = gov.balanceOf(otherAddr2);

    free(e, wad);

    mathint liveAfter = live();
    address hatAfter = hat();
    address slatesAfter = slates(anyB32, anyUint);
    bytes32 votesAfter = votes(anyAddr);
    mathint approvalsSlatesVotesSender0After = approvals(slatesVotesSender0);
    mathint approvalsSlatesVotesSender1After = approvals(slatesVotesSender1);
    mathint approvalsSlatesVotesSender2After = approvals(slatesVotesSender2);
    mathint approvalsSlatesVotesSender3After = approvals(slatesVotesSender3);
    mathint approvalsSlatesVotesSender4After = approvals(slatesVotesSender4);
    mathint approvalsSlatesVotesNotSenderAnyAfter = approvals(slatesNotSenderAny);
    mathint depositsSenderAfter = deposits(e.msg.sender);
    mathint depositsOtherAfter = deposits(otherAddr);
    mathint lastAfter = last(anyAddr);
    mathint govBalanceOfSenderAfter = gov.balanceOf(e.msg.sender);
    mathint govBalanceOfChiefAfter = gov.balanceOf(currentContract);
    mathint govBalanceOfOtherAfter = gov.balanceOf(otherAddr2);

    assert liveAfter == liveBefore, "free did not keep unchanged live";
    assert hatAfter == hatBefore, "free did not keep unchanged hat";
    assert slatesAfter == slatesBefore, "free did not keep unchanged every slates[x][y]";
    assert votesAfter == votesBefore, "free did not keep unchanged every votes[x]";
    assert lengthVotesSender >= 1 => approvalsSlatesVotesSender0After == approvalsSlatesVotesSender0Before - wad, "free did not decrease approvals[slatesVotesSender0] by wad";
    assert lengthVotesSender >= 2 => approvalsSlatesVotesSender1After == approvalsSlatesVotesSender1Before - wad, "free did not decrease approvals[slatesVotesSender1] by wad";
    assert lengthVotesSender >= 3 => approvalsSlatesVotesSender2After == approvalsSlatesVotesSender2Before - wad, "free did not decrease approvals[slatesVotesSender2] by wad";
    assert lengthVotesSender >= 4 => approvalsSlatesVotesSender3After == approvalsSlatesVotesSender3Before - wad, "free did not decrease approvals[slatesVotesSender3] by wad";
    assert lengthVotesSender == 5 => approvalsSlatesVotesSender4After == approvalsSlatesVotesSender4Before - wad, "free did not decrease approvals[slatesVotesSender4] by wad";
    assert approvalsSlatesVotesNotSenderAnyAfter == approvalsSlatesVotesNotSenderAnyBefore, "free did not keep unchanged the rest of approvals[x]";
    assert depositsSenderAfter == depositsSenderBefore - wad, "free did not decrease deposits[sender] by wad";
    assert depositsOtherAfter == depositsOtherBefore, "free did not keep unchanged the rest of deposits[x]";
    assert lastAfter == lastBefore, "free did not keep unchanged last[x]";
    assert govBalanceOfSenderAfter == govBalanceOfSenderBefore + wad, "free did not increase gov.balanceOf[sender] by wad";
    assert govBalanceOfChiefAfter == govBalanceOfChiefBefore - wad, "free did not decrease gov.balanceOf[chief] by wad";
    assert govBalanceOfOtherAfter == govBalanceOfOtherBefore, "free did not keep unchanged the rest of gov.balanceOf[x]";
}

// Verify revert rules on free
rule free_revert(uint256 wad) {
    env e;

    mathint maxYays = maxYays();
    require maxYays == 5;
    require gov.balanceOf(currentContract) >= wad;
    require gov.balanceOf(e.msg.sender) + wad < max_uint256;
    address addr0 = 0;
    require e.msg.sender != addr0 && e.msg.sender != gov;

    mathint lastSender = last(e.msg.sender);
    mathint depositsSender = deposits(e.msg.sender);
    bytes32 votesSender = votes(e.msg.sender);
    mathint lengthVotesSender = length(votesSender);
    require lengthVotesSender <= maxYays;
    address slatesVotesSender0 = lengthVotesSender >= 1 ? slates(votesSender, 0) : addr0; // Just any address as placeholder
    address slatesVotesSender1 = lengthVotesSender >= 2 ? slates(votesSender, 1) : addr0;
    address slatesVotesSender2 = lengthVotesSender >= 3 ? slates(votesSender, 2) : addr0;
    address slatesVotesSender3 = lengthVotesSender >= 4 ? slates(votesSender, 3) : addr0;
    address slatesVotesSender4 = lengthVotesSender == 5 ? slates(votesSender, 4) : addr0;
    require lengthVotesSender <= 1 || slatesVotesSender1 > slatesVotesSender0;
    require lengthVotesSender <= 2 || slatesVotesSender2 > slatesVotesSender1;
    require lengthVotesSender <= 3 || slatesVotesSender3 > slatesVotesSender2;
    require lengthVotesSender <= 4 || slatesVotesSender4 > slatesVotesSender3;
    mathint approvalsSlatesVotesSender0 = approvals(slatesVotesSender0);
    mathint approvalsSlatesVotesSender1 = approvals(slatesVotesSender1);
    mathint approvalsSlatesVotesSender2 = approvals(slatesVotesSender2);
    mathint approvalsSlatesVotesSender3 = approvals(slatesVotesSender3);
    mathint approvalsSlatesVotesSender4 = approvals(slatesVotesSender4);

    free@withrevert(e, wad);

    bool revert1 = e.msg.value > 0;
    bool revert2 = to_mathint(e.block.number) <= lastSender;
    bool revert3 = depositsSender < to_mathint(wad);
    bool revert4 = lengthVotesSender >= 1 && approvalsSlatesVotesSender0 < to_mathint(wad);
    bool revert5 = lengthVotesSender >= 2 && approvalsSlatesVotesSender1 < to_mathint(wad);
    bool revert6 = lengthVotesSender >= 3 && approvalsSlatesVotesSender2 < to_mathint(wad);
    bool revert7 = lengthVotesSender >= 4 && approvalsSlatesVotesSender3 < to_mathint(wad);
    bool revert8 = lengthVotesSender == 5 && approvalsSlatesVotesSender4 < to_mathint(wad);

    assert revert1 => lastReverted, "revert1 failed";
    assert revert2 => lastReverted, "revert2 failed";
    assert revert3 => lastReverted, "revert3 failed";
    assert revert4 => lastReverted, "revert4 failed";
    assert revert5 => lastReverted, "revert5 failed";
    assert revert6 => lastReverted, "revert6 failed";
    assert revert7 => lastReverted, "revert7 failed";
    assert revert8 => lastReverted, "revert8 failed";
    assert lastReverted => revert1 || revert2 || revert3 ||
                           revert4 || revert5 || revert6 ||
                           revert7 || revert8, "Revert rules are not covering all the cases";
}

// Verify correct storage changes for non reverting etch
rule etch(address[] yays) {
    env e;

    mathint maxYays = maxYays();
    require maxYays == 5;

    uint256 anyUint;
    address anyAddr;

    mathint yaysLength = yays.length;
    bytes32 slateYays = yaysLength <= maxYays ? aux.hashYays(yays) : to_bytes32(0); // To avoid an error on something that won't be used
    bytes32 otherB32;
    require otherB32 != slateYays;
    require to_mathint(length(slateYays)) <= maxYays; // Not possible to have an existing array larger than maxYays, but still needed for the prover

    mathint liveBefore = live();
    address hatBefore = hat();
    address slatesOtherAnyBefore = slates(otherB32, anyUint);
    bytes32 votesBefore = votes(anyAddr);
    mathint approvalsBefore = approvals(anyAddr);
    mathint depositsBefore = deposits(anyAddr);
    mathint lastBefore = last(anyAddr);

    etch(e, yays);

    mathint liveAfter = live();
    address hatAfter = hat();
    address addr0 = 0;
    mathint slatesSlateYaysLength = length(slateYays);
    address slatesSlateYays0 = yays.length >= 1 ? slates(slateYays, 0) : addr0; // Just any addr as it doesn't save it
    address slatesSlateYays1 = yays.length >= 2 ? slates(slateYays, 1) : addr0;
    address slatesSlateYays2 = yays.length >= 3 ? slates(slateYays, 2) : addr0;
    address slatesSlateYays3 = yays.length >= 4 ? slates(slateYays, 3) : addr0;
    address slatesSlateYays4 = yays.length == 5 ? slates(slateYays, 4) : addr0;
    address slatesOtherAnyAfter = slates(otherB32, anyUint);
    bytes32 votesAfter = votes(anyAddr);
    mathint approvalsAfter = approvals(anyAddr);
    mathint depositsAfter = deposits(anyAddr);
    mathint lastAfter = last(anyAddr);

    assert liveAfter == liveBefore, "etch did not keep unchanged live";
    assert hatAfter == hatBefore, "etch did not keep unchanged hat";
    assert slatesSlateYaysLength == yaysLength, "etch did not set slates[slateYays].length as yays.length";
    assert yays.length >= 1 => slatesSlateYays0 == yays[0], "etch did not set slates[slateYays][0] as yays[0]";
    assert yays.length >= 2 => slatesSlateYays1 == yays[1], "etch did not set slates[slateYays][1] as yays[1]";
    assert yays.length >= 3 => slatesSlateYays2 == yays[2], "etch did not set slates[slateYays][2] as yays[2]";
    assert yays.length >= 4 => slatesSlateYays3 == yays[3], "etch did not set slates[slateYays][3] as yays[3]";
    assert yays.length == 5 => slatesSlateYays4 == yays[4], "etch did not set slates[slateYays][4] as yays[4]";
    assert slatesOtherAnyAfter == slatesOtherAnyBefore, "etch did not keep unchanged the rest of slates[x][y]";
    assert votesAfter == votesBefore, "etch did not keep unchanged every votes[x]";
    assert approvalsAfter == approvalsBefore, "etch did not keep unchanged every approvals[x]";
    assert depositsAfter == depositsBefore, "etch did not keep unchanged every deposits[x]";
    assert lastAfter == lastBefore, "etch did not keep unchanged every last[x]";
}

// Verify revert rules on etch
rule etch_revert(address[] yays) {
    env e;

    mathint maxYays = maxYays();
    require maxYays == 5;

    bytes32 slateYays = to_mathint(yays.length) <= maxYays ? aux.hashYays(yays) : to_bytes32(0); // To avoid an error on something that won't be used
    require to_mathint(length(slateYays)) <= maxYays; // Not possible to have an existing array larger than maxYays, but still needed for the prover

    mathint yaysLength = yays.length;

    etch@withrevert(e, yays);

    bool revert1 = e.msg.value > 0;
    bool revert2 = yaysLength > maxYays;
    bool revert3 = yaysLength >= 2 && yays[0] >= yays[1];
    bool revert4 = yaysLength >= 3 && yays[1] >= yays[2];
    bool revert5 = yaysLength >= 4 && yays[2] >= yays[3];
    bool revert6 = yaysLength == 5 && yays[3] >= yays[4];

    assert revert1 => lastReverted, "revert1 failed";
    assert revert2 => lastReverted, "revert2 failed";
    assert revert3 => lastReverted, "revert3 failed";
    assert revert4 => lastReverted, "revert4 failed";
    assert revert5 => lastReverted, "revert5 failed";
    assert revert6 => lastReverted, "revert6 failed";
    assert lastReverted => revert1 || revert2 || revert3 ||
                           revert4 || revert5 || revert6, "Revert rules are not covering all the cases";
}

// Verify correct storage changes for non reverting vote
rule vote_yays(address[] yays) {
    env e;

    mathint maxYays = maxYays();
    require maxYays == 5;

    bytes32 anyB32;
    uint256 anyUint;
    address anyAddr;

    mathint yaysLength = to_mathint(yays.length);
    bytes32 slateYays = yaysLength <= maxYays ? aux.hashYays(yays) : to_bytes32(0); // To avoid an error on something that won't be used
    bytes32 otherB32;
    require otherB32 != slateYays;
    require to_mathint(length(slateYays)) <= maxYays; // Not possible to have an existing array larger than maxYays, but still needed for the prover

    address otherAddr;
    require otherAddr != e.msg.sender;

    mathint liveBefore = live();
    address hatBefore = hat();
    address slatesOtherAnyBefore = slates(otherB32, anyUint);
    bytes32 votesSenderBefore = votes(e.msg.sender);
    bytes32 votesOtherBefore = votes(otherAddr);
    mathint lengthVotesSender = length(votesSenderBefore);
    require lengthVotesSender <= maxYays;
    address addr0 = 0;
    address slatesVotesSender0 = lengthVotesSender >= 1 ? slates(votesSenderBefore, 0) : addr0; // Just any address as placeholder
    address slatesVotesSender1 = lengthVotesSender >= 2 ? slates(votesSenderBefore, 1) : addr0;
    address slatesVotesSender2 = lengthVotesSender >= 3 ? slates(votesSenderBefore, 2) : addr0;
    address slatesVotesSender3 = lengthVotesSender >= 4 ? slates(votesSenderBefore, 3) : addr0;
    address slatesVotesSender4 = lengthVotesSender == 5 ? slates(votesSenderBefore, 4) : addr0;

    // This is to avoid that the hash of the new voting array can collide with the hash of the prev existing voted (if not the same content)
    require lengthVotesSender != yaysLength => votesSenderBefore != slateYays;
    require lengthVotesSender == yaysLength && yays.length == 1 &&
            slatesVotesSender0 != yays[0]
            => votesSenderBefore != slateYays;
    require lengthVotesSender == yaysLength && yays.length == 2 &&
            (slatesVotesSender0 != yays[0] ||
             slatesVotesSender1 != yays[1])
            => votesSenderBefore != slateYays;
    require lengthVotesSender == yaysLength && yays.length == 3 &&
            (slatesVotesSender0 != yays[0] ||
             slatesVotesSender1 != yays[1] ||
             slatesVotesSender2 != yays[2])
            => votesSenderBefore != slateYays;
    require lengthVotesSender == yaysLength && yays.length == 4 &&
            (slatesVotesSender0 != yays[0] ||
             slatesVotesSender1 != yays[1] ||
             slatesVotesSender2 != yays[2] ||
             slatesVotesSender3 != yays[3])
            => votesSenderBefore != slateYays;
    require lengthVotesSender == yaysLength && yays.length == 5 &&
            (slatesVotesSender0 != yays[0] ||
             slatesVotesSender1 != yays[1] ||
             slatesVotesSender2 != yays[2] ||
             slatesVotesSender3 != yays[3] ||
             slatesVotesSender4 != yays[4])
            => votesSenderBefore != slateYays;
    //

    require lengthVotesSender <= 1 || slatesVotesSender1 > slatesVotesSender0;
    require lengthVotesSender <= 2 || slatesVotesSender2 > slatesVotesSender1;
    require lengthVotesSender <= 3 || slatesVotesSender3 > slatesVotesSender2;
    require lengthVotesSender <= 4 || slatesVotesSender4 > slatesVotesSender3;
    require yays.length <= 1 || yays[1] > yays[0];
    require yays.length <= 2 || yays[2] > yays[1];
    require yays.length <= 3 || yays[3] > yays[2];
    require yays.length <= 4 || yays[4] > yays[3];
    address slatesOtherAny;
    require (lengthVotesSender < 1 || slatesOtherAny != slatesVotesSender0) &&
            (lengthVotesSender < 2 || slatesOtherAny != slatesVotesSender1) &&
            (lengthVotesSender < 3 || slatesOtherAny != slatesVotesSender2) &&
            (lengthVotesSender < 4 || slatesOtherAny != slatesVotesSender3) &&
            (lengthVotesSender < 5 || slatesOtherAny != slatesVotesSender4);
    require (yays.length < 1 || slatesOtherAny != yays[0]) &&
            (yays.length < 2 || slatesOtherAny != yays[1]) &&
            (yays.length < 3 || slatesOtherAny != yays[2]) &&
            (yays.length < 4 || slatesOtherAny != yays[3]) &&
            (yays.length < 5 || slatesOtherAny != yays[4]);
    mathint approvalsSlatesVotesSender0Before = approvals(slatesVotesSender0);
    mathint approvalsSlatesVotesSender1Before = approvals(slatesVotesSender1);
    mathint approvalsSlatesVotesSender2Before = approvals(slatesVotesSender2);
    mathint approvalsSlatesVotesSender3Before = approvals(slatesVotesSender3);
    mathint approvalsSlatesVotesSender4Before = approvals(slatesVotesSender4);
    mathint approvalsYays0Before = approvals(yays[0]);
    mathint approvalsYays1Before = approvals(yays[1]);
    mathint approvalsYays2Before = approvals(yays[2]);
    mathint approvalsYays3Before = approvals(yays[3]);
    mathint approvalsYays4Before = approvals(yays[4]);
    mathint approvalsYaysNotSenderBefore = approvals(slatesOtherAny);
    mathint depositsSender = deposits(e.msg.sender);
    mathint depositsBefore = deposits(anyAddr);
    mathint lastBefore = last(anyAddr);

    vote(e, yays);

    mathint liveAfter = live();
    address hatAfter = hat();
    mathint lengthSlateYays = length(slateYays);
    address slatesSlateYays0 = yays.length >= 1 ? slates(slateYays, 0) : addr0; // Just any addr as it doesn't save it
    address slatesSlateYays1 = yays.length >= 2 ? slates(slateYays, 1) : addr0;
    address slatesSlateYays2 = yays.length >= 3 ? slates(slateYays, 2) : addr0;
    address slatesSlateYays3 = yays.length >= 4 ? slates(slateYays, 3) : addr0;
    address slatesSlateYays4 = yays.length == 5 ? slates(slateYays, 4) : addr0;
    address slatesOtherAnyAfter = slates(otherB32, anyUint);
    bytes32 votesSenderAfter = votes(e.msg.sender);
    bytes32 votesOtherAfter = votes(otherAddr);
    mathint approvalsSlatesVotesSender0After = approvals(slatesVotesSender0);
    mathint approvalsSlatesVotesSender1After = approvals(slatesVotesSender1);
    mathint approvalsSlatesVotesSender2After = approvals(slatesVotesSender2);
    mathint approvalsSlatesVotesSender3After = approvals(slatesVotesSender3);
    mathint approvalsSlatesVotesSender4After = approvals(slatesVotesSender4);
    mathint approvalsYays0After = approvals(yays[0]);
    mathint approvalsYays1After = approvals(yays[1]);
    mathint approvalsYays2After = approvals(yays[2]);
    mathint approvalsYays3After = approvals(yays[3]);
    mathint approvalsYays4After = approvals(yays[4]);
    mathint approvalsYaysNotSenderAfter = approvals(slatesOtherAny);
    mathint depositsAfter = deposits(anyAddr);
    mathint lastAfter = last(anyAddr);

    assert liveAfter == liveBefore, "vote did not keep unchanged live";
    assert hatAfter == hatBefore, "vote did not keep unchanged hat";
    assert lengthSlateYays == yaysLength, "vote did not set slates[slateYays].length as yays.length";
    assert yays.length >= 1 => slatesSlateYays0 == yays[0], "vote did not set slates[slateYays][0] as yays[0]";
    assert yays.length >= 2 => slatesSlateYays1 == yays[1], "vote did not set slates[slateYays][1] as yays[1]";
    assert yays.length >= 3 => slatesSlateYays2 == yays[2], "vote did not set slates[slateYays][2] as yays[2]";
    assert yays.length >= 4 => slatesSlateYays3 == yays[3], "vote did not set slates[slateYays][3] as yays[3]";
    assert yays.length == 5 => slatesSlateYays4 == yays[4], "vote did not set slates[slateYays][4] as yays[4]";
    assert slatesOtherAnyAfter == slatesOtherAnyBefore, "vote did not keep unchanged the rest of slates[x][y]";
    assert votesSenderAfter == slateYays, "vote did not set votes[sender] to slate";
    assert votesOtherAfter == votesOtherBefore, "vote did not keep unchanged the rest of votes[x]";
    assert lengthVotesSender >= 1 &&
           slatesVotesSender0 != yays[0] &&
           slatesVotesSender0 != yays[1] &&
           slatesVotesSender0 != yays[2] &&
           slatesVotesSender0 != yays[3] &&
           slatesVotesSender0 != yays[4]
           => approvalsSlatesVotesSender0After == approvalsSlatesVotesSender0Before - depositsSender, "vote did not decrease approvals[slatesVotesSender0] by depositsSender";
    assert lengthVotesSender >= 1 &&
           (yays.length >= 1 && slatesVotesSender0 == yays[0] ||
            yays.length >= 2 && slatesVotesSender0 == yays[1] ||
            yays.length >= 3 && slatesVotesSender0 == yays[2] ||
            yays.length >= 4 && slatesVotesSender0 == yays[3] ||
            yays.length == 5 && slatesVotesSender0 == yays[4])
           => approvalsSlatesVotesSender0After == approvalsSlatesVotesSender0Before, "vote did not keep unchanged approvals[slatesVotesSender0]";
    assert lengthVotesSender >= 2 &&
           slatesVotesSender1 != yays[0] &&
           slatesVotesSender1 != yays[1] &&
           slatesVotesSender1 != yays[2] &&
           slatesVotesSender1 != yays[3] &&
           slatesVotesSender1 != yays[4]
           => approvalsSlatesVotesSender1After == approvalsSlatesVotesSender1Before - depositsSender, "vote did not decrease approvals[slatesVotesSender1] by depositsSender";
    assert lengthVotesSender >= 2 &&
           (yays.length >= 1 && slatesVotesSender1 == yays[0] ||
            yays.length >= 2 && slatesVotesSender1 == yays[1] ||
            yays.length >= 3 && slatesVotesSender1 == yays[2] ||
            yays.length >= 4 && slatesVotesSender1 == yays[3] ||
            yays.length == 5 && slatesVotesSender1 == yays[4])
           => approvalsSlatesVotesSender1After == approvalsSlatesVotesSender1Before, "vote did not keep unchanged approvals[slatesVotesSender1]";
    assert lengthVotesSender >= 3 &&
           slatesVotesSender2 != yays[0] &&
           slatesVotesSender2 != yays[1] &&
           slatesVotesSender2 != yays[2] &&
           slatesVotesSender2 != yays[3] &&
           slatesVotesSender2 != yays[4]
           => approvalsSlatesVotesSender2After == approvalsSlatesVotesSender2Before - depositsSender, "vote did not decrease approvals[slatesVotesSender2] by depositsSender";
    assert lengthVotesSender >= 3 &&
           (yays.length >= 1 && slatesVotesSender2 == yays[0] ||
            yays.length >= 2 && slatesVotesSender2 == yays[1] ||
            yays.length >= 3 && slatesVotesSender2 == yays[2] ||
            yays.length >= 4 && slatesVotesSender2 == yays[3] ||
            yays.length == 5 && slatesVotesSender2 == yays[4])
           => approvalsSlatesVotesSender2After == approvalsSlatesVotesSender2Before, "vote did not keep unchanged approvals[slatesVotesSender2]";
    assert lengthVotesSender >= 4 &&
           slatesVotesSender3 != yays[0] &&
           slatesVotesSender3 != yays[1] &&
           slatesVotesSender3 != yays[2] &&
           slatesVotesSender3 != yays[3] &&
           slatesVotesSender3 != yays[4]
           => approvalsSlatesVotesSender3After == approvalsSlatesVotesSender3Before - depositsSender, "vote did not decrease approvals[slatesVotesSender3] by depositsSender";
    assert lengthVotesSender >= 4 &&
           (yays.length >= 1 && slatesVotesSender3 == yays[0] ||
            yays.length >= 2 && slatesVotesSender3 == yays[1] ||
            yays.length >= 3 && slatesVotesSender3 == yays[2] ||
            yays.length >= 4 && slatesVotesSender3 == yays[3] ||
            yays.length == 5 && slatesVotesSender3 == yays[4])
           => approvalsSlatesVotesSender3After == approvalsSlatesVotesSender3Before, "vote did not keep unchanged approvals[slatesVotesSender3]";
    assert lengthVotesSender == 5 &&
           slatesVotesSender4 != yays[0] &&
           slatesVotesSender4 != yays[1] &&
           slatesVotesSender4 != yays[2] &&
           slatesVotesSender4 != yays[3] &&
           slatesVotesSender4 != yays[4]
           => approvalsSlatesVotesSender4After == approvalsSlatesVotesSender4Before - depositsSender, "vote did not decrease approvals[slatesVotesSender4] by depositsSender";
    assert lengthVotesSender == 5 &&
           (yays.length >= 1 && slatesVotesSender4 == yays[0] ||
            yays.length >= 2 && slatesVotesSender4 == yays[1] ||
            yays.length >= 3 && slatesVotesSender4 == yays[2] ||
            yays.length >= 4 && slatesVotesSender4 == yays[3] ||
            yays.length == 5 && slatesVotesSender4 == yays[4])
           => approvalsSlatesVotesSender4After == approvalsSlatesVotesSender4Before, "vote did not keep unchanged approvals[slatesVotesSender4]";
    assert yays.length >= 1 &&
           yays[0] != slatesVotesSender0 &&
           yays[0] != slatesVotesSender1 &&
           yays[0] != slatesVotesSender2 &&
           yays[0] != slatesVotesSender3 &&
           yays[0] != slatesVotesSender4
           => approvalsYays0After == approvalsYays0Before + depositsSender, "vote did not increase approvals[yays0] by depositsSender";
    assert yays.length >= 2 &&
           yays[1] != slatesVotesSender0 &&
           yays[1] != slatesVotesSender1 &&
           yays[1] != slatesVotesSender2 &&
           yays[1] != slatesVotesSender3 &&
           yays[1] != slatesVotesSender4
           => approvalsYays1After == approvalsYays1Before + depositsSender, "vote did not increase approvals[yays1] by depositsSender";
    assert yays.length >= 3 &&
           yays[2] != slatesVotesSender0 &&
           yays[2] != slatesVotesSender1 &&
           yays[2] != slatesVotesSender2 &&
           yays[2] != slatesVotesSender3 &&
           yays[2] != slatesVotesSender4
           => approvalsYays2After == approvalsYays2Before + depositsSender, "vote did not increase approvals[yays2] by depositsSender";
    assert yays.length >= 4 &&
           yays[3] != slatesVotesSender0 &&
           yays[3] != slatesVotesSender1 &&
           yays[3] != slatesVotesSender2 &&
           yays[3] != slatesVotesSender3 &&
           yays[3] != slatesVotesSender4
           => approvalsYays3After == approvalsYays3Before + depositsSender, "vote did not increase approvals[yays3] by depositsSender";
    assert yays.length == 5 &&
           yays[4] != slatesVotesSender0 &&
           yays[4] != slatesVotesSender1 &&
           yays[4] != slatesVotesSender2 &&
           yays[4] != slatesVotesSender3 &&
           yays[4] != slatesVotesSender4
           => approvalsYays4After == approvalsYays4Before + depositsSender, "vote did not increase approvals[yays4] by depositsSender";
    assert approvalsYaysNotSenderAfter == approvalsYaysNotSenderBefore, "vote did not keep unchanged the rest of approvals[x]";
    assert depositsAfter == depositsBefore, "vote did not keep unchanged every deposits[x]";
    assert lastAfter == lastBefore, "vote did not keep unchanged every last[x]";
}

// Verify revert rules on vote
rule vote_yays_revert(address[] yays) {
    env e;

    mathint maxYays = maxYays();
    require maxYays == 5;

    mathint yaysLength = yays.length;
    bytes32 slateYays = yaysLength <= maxYays ? aux.hashYays(yays) : to_bytes32(0); // To avoid an error on something that won't be used
    require to_mathint(length(slateYays)) <= maxYays; // Not possible to have an existing array larger than maxYays, but still needed for the prover

    bytes32 votesSender = votes(e.msg.sender);
    mathint lengthVotesSender = length(votesSender);
    require lengthVotesSender <= maxYays;
    address addr0 = 0;
    address slatesVotesSender0 = lengthVotesSender >= 1 ? slates(votesSender, 0) : addr0; // Just any address as placeholder
    address slatesVotesSender1 = lengthVotesSender >= 2 ? slates(votesSender, 1) : addr0;
    address slatesVotesSender2 = lengthVotesSender >= 3 ? slates(votesSender, 2) : addr0;
    address slatesVotesSender3 = lengthVotesSender >= 4 ? slates(votesSender, 3) : addr0;
    address slatesVotesSender4 = lengthVotesSender == 5 ? slates(votesSender, 4) : addr0;
    require lengthVotesSender <= 1 || slatesVotesSender1 > slatesVotesSender0;
    require lengthVotesSender <= 2 || slatesVotesSender2 > slatesVotesSender1;
    require lengthVotesSender <= 3 || slatesVotesSender3 > slatesVotesSender2;
    require lengthVotesSender <= 4 || slatesVotesSender4 > slatesVotesSender3;
    mathint approvalsSlatesVotesSender0 = approvals(slatesVotesSender0);
    mathint approvalsSlatesVotesSender1 = approvals(slatesVotesSender1);
    mathint approvalsSlatesVotesSender2 = approvals(slatesVotesSender2);
    mathint approvalsSlatesVotesSender3 = approvals(slatesVotesSender3);
    mathint approvalsSlatesVotesSender4 = approvals(slatesVotesSender4);
    address yays0 = yaysLength >= 1 ? yays[0] : addr0; // Just any address as placeholder
    address yays1 = yaysLength >= 2 ? yays[1] : addr0;
    address yays2 = yaysLength >= 3 ? yays[2] : addr0;
    address yays3 = yaysLength >= 4 ? yays[3] : addr0;
    address yays4 = yaysLength == 5 ? yays[4] : addr0;
    require yaysLength <= 1 || yays1 > yays0;
    require yaysLength <= 2 || yays2 > yays1;
    require yaysLength <= 3 || yays3 > yays2;
    require yaysLength <= 4 || yays4 > yays3;
    mathint approvalsYays0 = approvals(yays0);
    mathint approvalsYays1 = approvals(yays1);
    mathint approvalsYays2 = approvals(yays2);
    mathint approvalsYays3 = approvals(yays3);
    mathint approvalsYays4 = approvals(yays4);
    mathint depositsSender = deposits(e.msg.sender);

    // This is to avoid that the hash of the new voting array can collide with the hash of the prev existing voted (if not the same content)
    require lengthVotesSender != yaysLength => votesSender != slateYays;
    require lengthVotesSender == yaysLength && yays.length == 1 &&
            slatesVotesSender0 != yays[0]
            => votesSender != slateYays;
    require lengthVotesSender == yaysLength && yays.length == 2 &&
            (slatesVotesSender0 != yays[0] ||
             slatesVotesSender1 != yays[1])
            => votesSender != slateYays;
    require lengthVotesSender == yaysLength && yays.length == 3 &&
            (slatesVotesSender0 != yays[0] ||
             slatesVotesSender1 != yays[1] ||
             slatesVotesSender2 != yays[2])
            => votesSender != slateYays;
    require lengthVotesSender == yaysLength && yays.length == 4 &&
            (slatesVotesSender0 != yays[0] ||
             slatesVotesSender1 != yays[1] ||
             slatesVotesSender2 != yays[2] ||
             slatesVotesSender3 != yays[3])
            => votesSender != slateYays;
    require lengthVotesSender == yaysLength && yays.length == 5 &&
            (slatesVotesSender0 != yays[0] ||
             slatesVotesSender1 != yays[1] ||
             slatesVotesSender2 != yays[2] ||
             slatesVotesSender3 != yays[3] ||
             slatesVotesSender4 != yays[4])
            => votesSender != slateYays;
    //

    address[] emptyArr;
    require(emptyArr.length == 0);
    bytes32 emptySlate = aux.hashYays(emptyArr);

    vote@withrevert(e, yays);

    bool revert1  = e.msg.value > 0;
    bool revert2  = yaysLength > maxYays;
    bool revert3  = yaysLength >= 2 && yays[0] >= yays[1];
    bool revert4  = yaysLength >= 3 && yays[1] >= yays[2];
    bool revert5  = yaysLength >= 4 && yays[2] >= yays[3];
    bool revert6  = yaysLength == 5 && yays[3] >= yays[4];
    bool revert7  = yaysLength == 0 && slateYays != emptySlate; // to_bytes32(0xc5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470);
    bool revert8  = lengthVotesSender >= 1 && approvalsSlatesVotesSender0 < depositsSender;
    bool revert9  = lengthVotesSender >= 2 && approvalsSlatesVotesSender1 < depositsSender;
    bool revert10 = lengthVotesSender >= 3 && approvalsSlatesVotesSender2 < depositsSender;
    bool revert11 = lengthVotesSender >= 4 && approvalsSlatesVotesSender3 < depositsSender;
    bool revert12 = lengthVotesSender == 5 && approvalsSlatesVotesSender4 < depositsSender;
    bool revert13 = yaysLength >= 1 &&
                    (lengthVotesSender < 1 || yays0 != slatesVotesSender0) &&
                    (lengthVotesSender < 2 || yays0 != slatesVotesSender1) &&
                    (lengthVotesSender < 3 || yays0 != slatesVotesSender2) &&
                    (lengthVotesSender < 4 || yays0 != slatesVotesSender3) &&
                    (lengthVotesSender < 5 || yays0 != slatesVotesSender4) &&
                    approvalsYays0 + depositsSender > max_uint256;
    bool revert14 = yaysLength >= 2 &&
                    (lengthVotesSender < 1 || yays1 != slatesVotesSender0) &&
                    (lengthVotesSender < 2 || yays1 != slatesVotesSender1) &&
                    (lengthVotesSender < 3 || yays1 != slatesVotesSender2) &&
                    (lengthVotesSender < 4 || yays1 != slatesVotesSender3) &&
                    (lengthVotesSender < 5 || yays1 != slatesVotesSender4) &&
                    approvalsYays1 + depositsSender > max_uint256;
    bool revert15 = yaysLength >= 3 &&
                    (lengthVotesSender < 1 || yays2 != slatesVotesSender0) &&
                    (lengthVotesSender < 2 || yays2 != slatesVotesSender1) &&
                    (lengthVotesSender < 3 || yays2 != slatesVotesSender2) &&
                    (lengthVotesSender < 4 || yays2 != slatesVotesSender3) &&
                    (lengthVotesSender < 5 || yays2 != slatesVotesSender4) &&
                    approvalsYays2 + depositsSender > max_uint256;
    bool revert16 = yaysLength >= 4 &&
                    (lengthVotesSender < 1 || yays3 != slatesVotesSender0) &&
                    (lengthVotesSender < 2 || yays3 != slatesVotesSender1) &&
                    (lengthVotesSender < 3 || yays3 != slatesVotesSender2) &&
                    (lengthVotesSender < 4 || yays3 != slatesVotesSender3) &&
                    (lengthVotesSender < 5 || yays3 != slatesVotesSender4) &&
                    approvalsYays3 + depositsSender > max_uint256;
    bool revert17 = yaysLength == 5 &&
                    (lengthVotesSender < 1 || yays4 != slatesVotesSender0) &&
                    (lengthVotesSender < 2 || yays4 != slatesVotesSender1) &&
                    (lengthVotesSender < 3 || yays4 != slatesVotesSender2) &&
                    (lengthVotesSender < 4 || yays4 != slatesVotesSender3) &&
                    (lengthVotesSender < 5 || yays4 != slatesVotesSender4) &&
                    approvalsYays4 + depositsSender > max_uint256;

    assert revert1  => lastReverted, "revert1 failed";
    assert revert2  => lastReverted, "revert2 failed";
    assert revert3  => lastReverted, "revert3 failed";
    assert revert4  => lastReverted, "revert4 failed";
    assert revert5  => lastReverted, "revert5 failed";
    assert revert6  => lastReverted, "revert6 failed";
    assert revert7  => lastReverted, "revert7 failed";
    assert revert8  => lastReverted, "revert8 failed";
    assert revert9  => lastReverted, "revert9 failed";
    assert revert10 => lastReverted, "revert10 failed";
    assert revert11 => lastReverted, "revert11 failed";
    assert revert12 => lastReverted, "revert12 failed";
    assert revert13 => lastReverted, "revert13 failed";
    assert revert14 => lastReverted, "revert14 failed";
    assert revert15 => lastReverted, "revert15 failed";
    assert revert16 => lastReverted, "revert12 failed";
    assert revert17 => lastReverted, "revert17 failed";
    assert lastReverted => revert1  || revert2  || revert3  ||
                           revert4  || revert5  || revert6  ||
                           revert7  || revert8  || revert9  ||
                           revert10 || revert11 || revert12 ||
                           revert13 || revert14 || revert15 ||
                           revert16 || revert17, "Revert rules are not covering all the cases";
}

// Verify correct storage changes for non reverting vote
rule vote_slate(bytes32 slate) {
    env e;

    mathint maxYays = maxYays();
    require maxYays == 5;

    bytes32 anyB32;
    uint256 anyUint;
    address anyAddr;

    address otherAddr;
    require otherAddr != e.msg.sender;

    mathint liveBefore = live();
    address hatBefore = hat();
    address slatesBefore = slates(anyB32, anyUint);
    bytes32 votesOtherBefore = votes(otherAddr);
    bytes32 votesSenderBefore = votes(e.msg.sender);
    mathint lengthVotesSender = length(votesSenderBefore);
    require lengthVotesSender <= maxYays;
    address addr0 = 0;
    address slatesVotesSender0 = lengthVotesSender >= 1 ? slates(votesSenderBefore, 0) : addr0; // Just any address as placeholder
    address slatesVotesSender1 = lengthVotesSender >= 2 ? slates(votesSenderBefore, 1) : addr0;
    address slatesVotesSender2 = lengthVotesSender >= 3 ? slates(votesSenderBefore, 2) : addr0;
    address slatesVotesSender3 = lengthVotesSender >= 4 ? slates(votesSenderBefore, 3) : addr0;
    address slatesVotesSender4 = lengthVotesSender == 5 ? slates(votesSenderBefore, 4) : addr0;
    require lengthVotesSender <= 1 || slatesVotesSender1 > slatesVotesSender0;
    require lengthVotesSender <= 2 || slatesVotesSender2 > slatesVotesSender1;
    require lengthVotesSender <= 3 || slatesVotesSender3 > slatesVotesSender2;
    require lengthVotesSender <= 4 || slatesVotesSender4 > slatesVotesSender3;
    mathint lengthSlate = length(slate);
    require lengthSlate <= maxYays;
    address slatesSlate0 = lengthSlate >= 1 ? slates(slate, 0) : addr0; // Just any address as placeholder
    address slatesSlate1 = lengthSlate >= 2 ? slates(slate, 1) : addr0;
    address slatesSlate2 = lengthSlate >= 3 ? slates(slate, 2) : addr0;
    address slatesSlate3 = lengthSlate >= 4 ? slates(slate, 3) : addr0;
    address slatesSlate4 = lengthSlate == 5 ? slates(slate, 4) : addr0;
    require lengthSlate <= 1 || slatesSlate1 > slatesSlate0;
    require lengthSlate <= 2 || slatesSlate2 > slatesSlate1;
    require lengthSlate <= 3 || slatesSlate3 > slatesSlate2;
    require lengthSlate <= 4 || slatesSlate4 > slatesSlate3;
    address slatesOtherAny;
    require (lengthVotesSender < 1 || slatesOtherAny != slatesVotesSender0) &&
            (lengthVotesSender < 2 || slatesOtherAny != slatesVotesSender1) &&
            (lengthVotesSender < 3 || slatesOtherAny != slatesVotesSender2) &&
            (lengthVotesSender < 4 || slatesOtherAny != slatesVotesSender3) &&
            (lengthVotesSender < 5 || slatesOtherAny != slatesVotesSender4);
    require (lengthSlate < 1 || slatesOtherAny != slatesSlate0) &&
            (lengthSlate < 2 || slatesOtherAny != slatesSlate1) &&
            (lengthSlate < 3 || slatesOtherAny != slatesSlate2) &&
            (lengthSlate < 4 || slatesOtherAny != slatesSlate3) &&
            (lengthSlate < 5 || slatesOtherAny != slatesSlate4);
    mathint approvalsSlatesVotesSender0Before = approvals(slatesVotesSender0);
    mathint approvalsSlatesVotesSender1Before = approvals(slatesVotesSender1);
    mathint approvalsSlatesVotesSender2Before = approvals(slatesVotesSender2);
    mathint approvalsSlatesVotesSender3Before = approvals(slatesVotesSender3);
    mathint approvalsSlatesVotesSender4Before = approvals(slatesVotesSender4);
    mathint approvalsSlatesSlate0Before = approvals(slatesSlate0);
    mathint approvalsSlatesSlate1Before = approvals(slatesSlate1);
    mathint approvalsSlatesSlate2Before = approvals(slatesSlate2);
    mathint approvalsSlatesSlate3Before = approvals(slatesSlate3);
    mathint approvalsSlatesSlate4Before = approvals(slatesSlate4);
    mathint approvalsSlatesOtherAnyBefore = approvals(slatesOtherAny);
    mathint depositsSender = deposits(e.msg.sender);
    mathint depositsBefore = deposits(anyAddr);
    mathint lastBefore = last(anyAddr);

    vote(e, slate);

    mathint liveAfter = live();
    address hatAfter = hat();
    address slatesAfter = slates(anyB32, anyUint);
    bytes32 votesSenderAfter = votes(e.msg.sender);
    bytes32 votesOtherAfter = votes(otherAddr);
    mathint approvalsSlatesVotesSender0After = approvals(slatesVotesSender0);
    mathint approvalsSlatesVotesSender1After = approvals(slatesVotesSender1);
    mathint approvalsSlatesVotesSender2After = approvals(slatesVotesSender2);
    mathint approvalsSlatesVotesSender3After = approvals(slatesVotesSender3);
    mathint approvalsSlatesVotesSender4After = approvals(slatesVotesSender4);
    mathint approvalsSlatesSlate0After = approvals(slatesSlate0);
    mathint approvalsSlatesSlate1After = approvals(slatesSlate1);
    mathint approvalsSlatesSlate2After = approvals(slatesSlate2);
    mathint approvalsSlatesSlate3After = approvals(slatesSlate3);
    mathint approvalsSlatesSlate4After = approvals(slatesSlate4);
    mathint approvalsSlatesOtherAnyAfter = approvals(slatesOtherAny);
    mathint depositsAfter = deposits(anyAddr);
    mathint lastAfter = last(anyAddr);

    assert liveAfter == liveBefore, "vote did not keep unchanged live";
    assert hatAfter == hatBefore, "vote did not keep unchanged hat";
    assert slatesAfter == slatesBefore, "vote did not keep unchanged every slates[x][y]";
    assert votesSenderAfter == slate, "vote did not set votes[sender] to slate";
    assert votesOtherAfter == votesOtherBefore, "vote did not keep unchanged the rest of votes[x]";
    assert lengthVotesSender >= 1 &&
           slatesVotesSender0 != slatesSlate0 &&
           slatesVotesSender0 != slatesSlate1 &&
           slatesVotesSender0 != slatesSlate2 &&
           slatesVotesSender0 != slatesSlate3 &&
           slatesVotesSender0 != slatesSlate4
           => approvalsSlatesVotesSender0After == approvalsSlatesVotesSender0Before - depositsSender, "vote did not decrease approvals[slatesVotesSender0] by depositsSender";
    assert lengthVotesSender >= 1 &&
           (lengthSlate >= 1 && slatesVotesSender0 == slatesSlate0 ||
            lengthSlate >= 2 && slatesVotesSender0 == slatesSlate1 ||
            lengthSlate >= 3 && slatesVotesSender0 == slatesSlate2 ||
            lengthSlate >= 4 && slatesVotesSender0 == slatesSlate3 ||
            lengthSlate == 5 && slatesVotesSender0 == slatesSlate4)
           => approvalsSlatesVotesSender0After == approvalsSlatesVotesSender0Before, "vote did not keep unchanged approvals[slatesVotesSender0]";
    assert lengthVotesSender >= 2 &&
           slatesVotesSender1 != slatesSlate0 &&
           slatesVotesSender1 != slatesSlate1 &&
           slatesVotesSender1 != slatesSlate2 &&
           slatesVotesSender1 != slatesSlate3 &&
           slatesVotesSender1 != slatesSlate4
           => approvalsSlatesVotesSender1After == approvalsSlatesVotesSender1Before - depositsSender, "vote did not decrease approvals[slatesVotesSender1] by depositsSender";
    assert lengthVotesSender >= 2 &&
           (lengthSlate >= 1 && slatesVotesSender1 == slatesSlate0 ||
            lengthSlate >= 2 && slatesVotesSender1 == slatesSlate1 ||
            lengthSlate >= 3 && slatesVotesSender1 == slatesSlate2 ||
            lengthSlate >= 4 && slatesVotesSender1 == slatesSlate3 ||
            lengthSlate == 5 && slatesVotesSender1 == slatesSlate4)
           => approvalsSlatesVotesSender1After == approvalsSlatesVotesSender1Before, "vote did not keep unchanged approvals[slatesVotesSender1]";
    assert lengthVotesSender >= 3 &&
           slatesVotesSender2 != slatesSlate0 &&
           slatesVotesSender2 != slatesSlate1 &&
           slatesVotesSender2 != slatesSlate2 &&
           slatesVotesSender2 != slatesSlate3 &&
           slatesVotesSender2 != slatesSlate4
           => approvalsSlatesVotesSender2After == approvalsSlatesVotesSender2Before - depositsSender, "vote did not decrease approvals[slatesVotesSender2] by depositsSender";
    assert lengthVotesSender >= 3 &&
           (lengthSlate >= 1 && slatesVotesSender2 == slatesSlate0 ||
            lengthSlate >= 2 && slatesVotesSender2 == slatesSlate1 ||
            lengthSlate >= 3 && slatesVotesSender2 == slatesSlate2 ||
            lengthSlate >= 4 && slatesVotesSender2 == slatesSlate3 ||
            lengthSlate == 5 && slatesVotesSender2 == slatesSlate4)
           => approvalsSlatesVotesSender2After == approvalsSlatesVotesSender2Before, "vote did not keep unchanged approvals[slatesVotesSender2]";
    assert lengthVotesSender >= 4 &&
           slatesVotesSender3 != slatesSlate0 &&
           slatesVotesSender3 != slatesSlate1 &&
           slatesVotesSender3 != slatesSlate2 &&
           slatesVotesSender3 != slatesSlate3 &&
           slatesVotesSender3 != slatesSlate4
           => approvalsSlatesVotesSender3After == approvalsSlatesVotesSender3Before - depositsSender, "vote did not decrease approvals[slatesVotesSender3] by depositsSender";
    assert lengthVotesSender >= 4 &&
           (lengthSlate >= 1 && slatesVotesSender3 == slatesSlate0 ||
            lengthSlate >= 2 && slatesVotesSender3 == slatesSlate1 ||
            lengthSlate >= 3 && slatesVotesSender3 == slatesSlate2 ||
            lengthSlate >= 4 && slatesVotesSender3 == slatesSlate3 ||
            lengthSlate == 5 && slatesVotesSender3 == slatesSlate4)
           => approvalsSlatesVotesSender3After == approvalsSlatesVotesSender3Before, "vote did not keep unchanged approvals[slatesVotesSender3]";
    assert lengthVotesSender == 5 &&
           slatesVotesSender4 != slatesSlate0 &&
           slatesVotesSender4 != slatesSlate1 &&
           slatesVotesSender4 != slatesSlate2 &&
           slatesVotesSender4 != slatesSlate3 &&
           slatesVotesSender4 != slatesSlate4
           => approvalsSlatesVotesSender4After == approvalsSlatesVotesSender4Before - depositsSender, "vote did not decrease approvals[slatesVotesSender4] by depositsSender";
    assert lengthVotesSender == 5 &&
           (lengthSlate >= 1 && slatesVotesSender4 == slatesSlate0 ||
            lengthSlate >= 2 && slatesVotesSender4 == slatesSlate1 ||
            lengthSlate >= 3 && slatesVotesSender4 == slatesSlate2 ||
            lengthSlate >= 4 && slatesVotesSender4 == slatesSlate3 ||
            lengthSlate == 5 && slatesVotesSender4 == slatesSlate4)
           => approvalsSlatesVotesSender4After == approvalsSlatesVotesSender4Before, "vote did not keep unchanged approvals[slatesVotesSender4]";
    assert lengthSlate >= 1 &&
           slatesSlate0 != slatesVotesSender0 &&
           slatesSlate0 != slatesVotesSender1 &&
           slatesSlate0 != slatesVotesSender2 &&
           slatesSlate0 != slatesVotesSender3 &&
           slatesSlate0 != slatesVotesSender4
           => approvalsSlatesSlate0After == approvalsSlatesSlate0Before + depositsSender, "vote did not increase approvals[slatesSlate0] by depositsSender";
    assert lengthSlate >= 2 &&
           slatesSlate1 != slatesVotesSender0 &&
           slatesSlate1 != slatesVotesSender1 &&
           slatesSlate1 != slatesVotesSender2 &&
           slatesSlate1 != slatesVotesSender3 &&
           slatesSlate1 != slatesVotesSender4
           => approvalsSlatesSlate1After == approvalsSlatesSlate1Before + depositsSender, "vote did not increase approvals[slatesSlate1] by depositsSender";
    assert lengthSlate >= 3 &&
           slatesSlate2 != slatesVotesSender0 &&
           slatesSlate2 != slatesVotesSender1 &&
           slatesSlate2 != slatesVotesSender2 &&
           slatesSlate2 != slatesVotesSender3 &&
           slatesSlate2 != slatesVotesSender4
           => approvalsSlatesSlate2After == approvalsSlatesSlate2Before + depositsSender, "vote did not increase approvals[slatesSlate2] by depositsSender";
    assert lengthSlate >= 4 &&
           slatesSlate3 != slatesVotesSender0 &&
           slatesSlate3 != slatesVotesSender1 &&
           slatesSlate3 != slatesVotesSender2 &&
           slatesSlate3 != slatesVotesSender3 &&
           slatesSlate3 != slatesVotesSender4
           => approvalsSlatesSlate3After == approvalsSlatesSlate3Before + depositsSender, "vote did not increase approvals[slatesSlate3] by depositsSender";
    assert lengthSlate == 5 &&
           slatesSlate4 != slatesVotesSender0 &&
           slatesSlate4 != slatesVotesSender1 &&
           slatesSlate4 != slatesVotesSender2 &&
           slatesSlate4 != slatesVotesSender3 &&
           slatesSlate4 != slatesVotesSender4
           => approvalsSlatesSlate4After == approvalsSlatesSlate4Before + depositsSender, "vote did not increase approvals[newYaysSender4] by depositsSender";
    assert approvalsSlatesOtherAnyAfter == approvalsSlatesOtherAnyBefore, "vote did not keep unchanged the rest of approvals[x]";
    assert depositsAfter == depositsBefore, "vote did not keep unchanged every deposits[x]";
    assert lastAfter == lastBefore, "vote did not keep unchanged every last[x]";
}

// Verify revert rules on vote
rule vote_slate_revert(bytes32 slate) {
    env e;

    mathint maxYays = maxYays();
    require maxYays == 5;

    bytes32 votesSender = votes(e.msg.sender);
    mathint lengthVotesSender = length(votesSender);
    require lengthVotesSender <= maxYays;
    address addr0 = 0;
    address slatesVotesSender0 = lengthVotesSender >= 1 ? slates(votesSender, 0) : addr0; // Just any address as placeholder
    address slatesVotesSender1 = lengthVotesSender >= 2 ? slates(votesSender, 1) : addr0;
    address slatesVotesSender2 = lengthVotesSender >= 3 ? slates(votesSender, 2) : addr0;
    address slatesVotesSender3 = lengthVotesSender >= 4 ? slates(votesSender, 3) : addr0;
    address slatesVotesSender4 = lengthVotesSender == 5 ? slates(votesSender, 4) : addr0;
    require lengthVotesSender <= 1 || slatesVotesSender1 > slatesVotesSender0;
    require lengthVotesSender <= 2 || slatesVotesSender2 > slatesVotesSender1;
    require lengthVotesSender <= 3 || slatesVotesSender3 > slatesVotesSender2;
    require lengthVotesSender <= 4 || slatesVotesSender4 > slatesVotesSender3;
    mathint approvalsSlatesVotesSender0 = approvals(slatesVotesSender0);
    mathint approvalsSlatesVotesSender1 = approvals(slatesVotesSender1);
    mathint approvalsSlatesVotesSender2 = approvals(slatesVotesSender2);
    mathint approvalsSlatesVotesSender3 = approvals(slatesVotesSender3);
    mathint approvalsSlatesVotesSender4 = approvals(slatesVotesSender4);
    mathint lengthSlate = length(slate);
    require lengthSlate <= 5; // Not possible to have an existing array larger than maxYays, but still needed for the prover
    address slatesSlate0 = lengthSlate >= 1 ? slates(slate, 0) : addr0; // Just any address as placeholder
    address slatesSlate1 = lengthSlate >= 2 ? slates(slate, 1) : addr0;
    address slatesSlate2 = lengthSlate >= 3 ? slates(slate, 2) : addr0;
    address slatesSlate3 = lengthSlate >= 4 ? slates(slate, 3) : addr0;
    address slatesSlate4 = lengthSlate == 5 ? slates(slate, 4) : addr0;
    require lengthSlate <= 1 || slatesSlate1 > slatesSlate0;
    require lengthSlate <= 2 || slatesSlate2 > slatesSlate1;
    require lengthSlate <= 3 || slatesSlate3 > slatesSlate2;
    require lengthSlate <= 4 || slatesSlate4 > slatesSlate3;
    mathint approvalsSlatesSlate0 = approvals(slatesSlate0);
    mathint approvalsSlatesSlate1 = approvals(slatesSlate1);
    mathint approvalsSlatesSlate2 = approvals(slatesSlate2);
    mathint approvalsSlatesSlate3 = approvals(slatesSlate3);
    mathint approvalsSlatesSlate4 = approvals(slatesSlate4);
    mathint depositsSender = deposits(e.msg.sender);

    address[] emptyArr;
    require(emptyArr.length == 0);
    bytes32 emptySlate = aux.hashYays(emptyArr);

    vote@withrevert(e, slate);

    bool revert1  = e.msg.value > 0;
    bool revert2  = lengthSlate == 0 && slate != emptySlate; // to_bytes32(0xc5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470);
    bool revert3  = lengthVotesSender >= 1 && approvalsSlatesVotesSender0 < depositsSender;
    bool revert4  = lengthVotesSender >= 2 && approvalsSlatesVotesSender1 < depositsSender;
    bool revert5  = lengthVotesSender >= 3 && approvalsSlatesVotesSender2 < depositsSender;
    bool revert6  = lengthVotesSender >= 4 && approvalsSlatesVotesSender3 < depositsSender;
    bool revert7  = lengthVotesSender == 5 && approvalsSlatesVotesSender4 < depositsSender;
    bool revert8  = lengthSlate >= 1 &&
                    (lengthVotesSender < 1 || slatesSlate0 != slatesVotesSender0) &&
                    (lengthVotesSender < 2 || slatesSlate0 != slatesVotesSender1) &&
                    (lengthVotesSender < 3 || slatesSlate0 != slatesVotesSender2) &&
                    (lengthVotesSender < 4 || slatesSlate0 != slatesVotesSender3) &&
                    (lengthVotesSender < 5 || slatesSlate0 != slatesVotesSender4) &&
                    approvalsSlatesSlate0 + depositsSender > max_uint256;
    bool revert9  = lengthSlate >= 2 &&
                    (lengthVotesSender < 1 || slatesSlate1 != slatesVotesSender0) &&
                    (lengthVotesSender < 2 || slatesSlate1 != slatesVotesSender1) &&
                    (lengthVotesSender < 3 || slatesSlate1 != slatesVotesSender2) &&
                    (lengthVotesSender < 4 || slatesSlate1 != slatesVotesSender3) &&
                    (lengthVotesSender < 5 || slatesSlate1 != slatesVotesSender4) &&
                    approvalsSlatesSlate1 + depositsSender > max_uint256;
    bool revert10 = lengthSlate >= 3 &&
                    (lengthVotesSender < 1 || slatesSlate2 != slatesVotesSender0) &&
                    (lengthVotesSender < 2 || slatesSlate2 != slatesVotesSender1) &&
                    (lengthVotesSender < 3 || slatesSlate2 != slatesVotesSender2) &&
                    (lengthVotesSender < 4 || slatesSlate2 != slatesVotesSender3) &&
                    (lengthVotesSender < 5 || slatesSlate2 != slatesVotesSender4) &&
                    approvalsSlatesSlate2 + depositsSender > max_uint256;
    bool revert11 = lengthSlate >= 4 &&
                    (lengthVotesSender < 1 || slatesSlate3 != slatesVotesSender0) &&
                    (lengthVotesSender < 2 || slatesSlate3 != slatesVotesSender1) &&
                    (lengthVotesSender < 3 || slatesSlate3 != slatesVotesSender2) &&
                    (lengthVotesSender < 4 || slatesSlate3 != slatesVotesSender3) &&
                    (lengthVotesSender < 5 || slatesSlate3 != slatesVotesSender4) &&
                    approvalsSlatesSlate3 + depositsSender > max_uint256;
    bool revert12 = lengthSlate == 5 &&
                    (lengthVotesSender < 1 || slatesSlate4 != slatesVotesSender0) &&
                    (lengthVotesSender < 2 || slatesSlate4 != slatesVotesSender1) &&
                    (lengthVotesSender < 3 || slatesSlate4 != slatesVotesSender2) &&
                    (lengthVotesSender < 4 || slatesSlate4 != slatesVotesSender3) &&
                    (lengthVotesSender < 5 || slatesSlate4 != slatesVotesSender4) &&
                    approvalsSlatesSlate4 + depositsSender > max_uint256;

    assert revert1  => lastReverted, "revert1 failed";
    assert revert2  => lastReverted, "revert2 failed";
    assert revert3  => lastReverted, "revert3 failed";
    assert revert4  => lastReverted, "revert4 failed";
    assert revert5  => lastReverted, "revert5 failed";
    assert revert6  => lastReverted, "revert6 failed";
    assert revert7  => lastReverted, "revert7 failed";
    assert revert8  => lastReverted, "revert8 failed";
    assert revert9  => lastReverted, "revert9 failed";
    assert revert10 => lastReverted, "revert10 failed";
    assert revert11 => lastReverted, "revert11 failed";
    assert revert12 => lastReverted, "revert12 failed";
    assert lastReverted => revert1  || revert2  || revert3 ||
                           revert4  || revert5  || revert6 ||
                           revert7  || revert8  || revert9 ||
                           revert10 || revert11 || revert12, "Revert rules are not covering all the cases";
}

// Verify correct storage changes for non reverting launch
rule lift(address whom) {
    env e;

    bytes32 anyB32;
    uint256 anyUint;
    address anyAddr;

    mathint liveBefore = live();
    address slatesBefore = slates(anyB32, anyUint);
    bytes32 votesBefore = votes(anyAddr);
    mathint approvalsBefore = approvals(anyAddr);
    mathint depositsBefore = deposits(anyAddr);
    mathint lastBefore = last(anyAddr);

    lift(e, whom);

    mathint liveAfter = live();
    address hatAfter = hat();
    address slatesAfter = slates(anyB32, anyUint);
    bytes32 votesAfter = votes(anyAddr);
    mathint approvalsAfter = approvals(anyAddr);
    mathint depositsAfter = deposits(anyAddr);
    mathint lastAfter = last(anyAddr);

    assert liveAfter == liveBefore, "lift did not keep unchanged live";
    assert hatAfter == whom, "lift did not set hat to whom";
    assert slatesAfter == slatesBefore, "lift did not keep unchanged every slates[x][y]";
    assert votesAfter == votesBefore, "lift did not keep unchanged every votes[x]";
    assert approvalsAfter == approvalsBefore, "lift did not keep unchanged every approvals[x]";
    assert depositsAfter == depositsBefore, "lift did not keep unchanged every deposits[x]";
    assert lastAfter == lastBefore, "lift did not keep unchanged every last[x]";
}

// Verify revert rules on lift
rule lift_revert(address whom) {
    env e;

    address hat = hat();
    mathint approvalsWhom = approvals(whom);
    mathint approvalsHat = approvals(hat);

    lift@withrevert(e, whom);

    bool revert1 = e.msg.value > 0;
    bool revert2 = approvalsWhom <= approvalsHat;

    assert revert1 => lastReverted, "revert1 failed";
    assert revert2 => lastReverted, "revert2 failed";
    assert lastReverted => revert1 || revert2, "Revert rules are not covering all the cases";
}
