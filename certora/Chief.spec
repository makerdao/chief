// Chief.spec

using TokenMock as gov;
using Auxiliar as aux;

methods {
    function live() external returns (uint256) envfree;
    function hat() external returns (address) envfree;
    function slates(bytes32, uint256) external returns (address) envfree;
    function votes(address) external returns (bytes32) envfree;
    function approvals(address) external returns (uint256) envfree;
    function deposits(address) external returns (uint256) envfree;
    function last() external returns (uint256) envfree;
    function gov() external returns (address) envfree;
    function maxYays() external returns (uint256) envfree;
    function launchThreshold() external returns (uint256) envfree;
    function EMPTY_SLATE() external returns (bytes32) envfree;
    function liftCooldown() external returns (uint256) envfree;
    function length(bytes32) external returns (uint256) envfree;
    function GOV() external returns (address) envfree;
    function MAX_YAYS() external returns (uint256) envfree;
    function gov.allowance(address, address) external returns (uint256) envfree;
    function gov.balanceOf(address) external returns (uint256) envfree;
    function aux.hashYays(address[]) external returns (bytes32) envfree;
}

// Verify no more entry points exist
rule entryPoints(method f) filtered { f -> !f.isView } {
    env e;

    mathint maxYays = maxYays();
    require maxYays == 5;

    calldataarg args;
    f(e, args);

    assert f.selector == sig:launch().selector ||
           f.selector == sig:lock(uint256).selector ||
           f.selector == sig:free(uint256).selector ||
           f.selector == sig:etch(address[]).selector ||
           f.selector == sig:vote(address[]).selector ||
           f.selector == sig:vote(bytes32).selector ||
           f.selector == sig:lift(address).selector;
}

// Verify that each storage layout is only modified in the corresponding functions
rule storageAffected(method f) {
    env e;

    mathint maxYays = maxYays();
    require maxYays == 5;

    bytes32 anyBytes32;
    uint256 anyUint256;
    address anyAddr;

    mathint liveBefore = live();
    address hatBefore = hat();
    address slatesBefore = slates(anyBytes32, anyUint256);
    bytes32 votesBefore = votes(anyAddr);
    mathint approvalsBefore = approvals(anyAddr);
    mathint depositsBefore = deposits(anyAddr);
    mathint lastBefore = last();
    mathint govBalanceOfBefore = gov.balanceOf(anyAddr);

    calldataarg args;
    f(e, args);

    mathint liveAfter = live();
    address hatAfter = hat();
    address slatesAfter = slates(anyBytes32, anyUint256);
    bytes32 votesAfter = votes(anyAddr);
    mathint approvalsAfter = approvals(anyAddr);
    mathint depositsAfter = deposits(anyAddr);
    mathint lastAfter = last();
    mathint govBalanceOfAfter = gov.balanceOf(anyAddr);

    assert liveAfter != liveBefore => f.selector == sig:launch().selector, "Assert 1";
    assert hatAfter != hatBefore => f.selector == sig:lift(address).selector, "Assert 2";
    assert slatesAfter != slatesBefore => f.selector == sig:etch(address[]).selector || f.selector == sig:vote(address[]).selector, "Assert 3";
    assert votesAfter != votesBefore => f.selector == sig:vote(address[]).selector || f.selector == sig:vote(bytes32).selector, "Assert 4";
    assert approvalsAfter != approvalsBefore => f.selector == sig:lock(uint256).selector || f.selector == sig:free(uint256).selector || f.selector == sig:vote(address[]).selector || f.selector == sig:vote(bytes32).selector, "Assert 5";
    assert depositsAfter != depositsBefore => f.selector == sig:lock(uint256).selector || f.selector == sig:free(uint256).selector, "Assert 6";
    assert lastAfter != lastBefore => f.selector == sig:launch().selector || f.selector == sig:lift(address).selector, "Assert 7";
    assert govBalanceOfAfter != govBalanceOfBefore => f.selector == sig:lock(uint256).selector || f.selector == sig:free(uint256).selector, "Assert 8";
}

// Verify correct value of EMPTY_SLATE
rule emptySlateGetter() {
    address[] emptyArr;
    require(emptyArr.length == 0);
    bytes32 emptySlate = aux.hashYays(emptyArr);

    assert EMPTY_SLATE() == emptySlate, "Assert 1";
}

// Verify correct behavior of old getters
rule compatibilityGetters() {
    assert GOV() == gov(), "Assert 1";
    assert MAX_YAYS() == maxYays(), "Assert 2";
}

// Verify correct storage changes for non reverting launch
rule launch() {
    env e;

    launch(e);

    mathint liveAfter = live();
    mathint lastAfter = last();

    assert liveAfter == 1, "Assert 1";
    assert lastAfter == e.block.number, "Assert 2";
}

// Verify revert rules on launch
rule launch_revert() {
    env e;

    mathint live = live();
    address hat = hat();
    mathint approvalsAddr0 = approvals(0);
    mathint last = last();
    mathint launchThreshold = launchThreshold();

    launch@withrevert(e);

    bool revert1 = e.msg.value > 0;
    bool revert2 = live != 0;
    bool revert3 = hat != 0;
    bool revert4 = approvalsAddr0 < launchThreshold;

    assert lastReverted <=> revert1 || revert2 || revert3 ||
                            revert4, "Revert rules failed";
}

// Verify correct storage changes for non reverting lock
rule lock(uint256 wad) {
    env e;

    require e.msg.sender != currentContract;

    mathint maxYays = maxYays();
    require maxYays == 5;

    address otherAddr;
    require otherAddr != e.msg.sender;

    address otherAddr2;
    require otherAddr2 != e.msg.sender && otherAddr2 != currentContract;

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
    mathint govBalanceOfSenderBefore = gov.balanceOf(e.msg.sender);
    mathint govBalanceOfChiefBefore = gov.balanceOf(currentContract);
    mathint govBalanceOfOtherBefore = gov.balanceOf(otherAddr2);

    lock(e, wad);

    mathint approvalsSlatesSender0After = approvals(slatesVotesSender0);
    mathint approvalsSlatesSender1After = approvals(slatesVotesSender1);
    mathint approvalsSlatesSender2After = approvals(slatesVotesSender2);
    mathint approvalsSlatesSender3After = approvals(slatesVotesSender3);
    mathint approvalsSlatesSender4After = approvals(slatesVotesSender4);
    mathint approvalsSlatesNotSenderAnyAfter = approvals(slatessNotSenderAny);
    mathint depositsSenderAfter = deposits(e.msg.sender);
    mathint depositsOtherAfter = deposits(otherAddr);
    mathint govBalanceOfSenderAfter = gov.balanceOf(e.msg.sender);
    mathint govBalanceOfChiefAfter = gov.balanceOf(currentContract);
    mathint govBalanceOfOtherAfter = gov.balanceOf(otherAddr2);

    assert lengthVotesSender >= 1 => approvalsSlatesSender0After == approvalsSlatesSender0Before + wad, "Assert 1";
    assert lengthVotesSender >= 2 => approvalsSlatesSender1After == approvalsSlatesSender1Before + wad, "Assert 2";
    assert lengthVotesSender >= 3 => approvalsSlatesSender2After == approvalsSlatesSender2Before + wad, "Assert 3";
    assert lengthVotesSender >= 4 => approvalsSlatesSender3After == approvalsSlatesSender3Before + wad, "Assert 4";
    assert lengthVotesSender == 5 => approvalsSlatesSender4After == approvalsSlatesSender4Before + wad, "Assert 5";
    assert approvalsSlatesNotSenderAnyAfter == approvalsSlatesNotSenderAnyBefore, "Assert 6";
    assert depositsSenderAfter == depositsSenderBefore + wad, "Assert 7";
    assert depositsOtherAfter == depositsOtherBefore, "Assert 8";
    assert govBalanceOfSenderAfter == govBalanceOfSenderBefore - wad, "Assert 9";
    assert govBalanceOfChiefAfter == govBalanceOfChiefBefore + wad, "Assert 10";
    assert govBalanceOfOtherAfter == govBalanceOfOtherBefore, "Assert 11";
}

// Verify revert rules on lock
rule lock_revert(uint256 wad) {
    env e;

    mathint maxYays = maxYays();
    require maxYays == 5;
    require gov.balanceOf(e.msg.sender) >= wad;
    require gov.allowance(e.msg.sender, currentContract) >= wad;
    require gov.balanceOf(currentContract) + wad <= max_uint256;

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

    assert lastReverted <=> revert1 || revert2 || revert3 ||
                            revert4 || revert5 || revert6 ||
                            revert7, "Revert rules failed";
}

// Verify correct storage changes for non reverting free
rule free(uint256 wad) {
    env e;

    require e.msg.sender != currentContract;

    mathint maxYays = maxYays();
    require maxYays == 5;

    address otherAddr;
    require otherAddr != e.msg.sender;

    address otherAddr2;
    require otherAddr2 != e.msg.sender && otherAddr2 != currentContract;

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
    mathint govBalanceOfSenderBefore = gov.balanceOf(e.msg.sender);
    mathint govBalanceOfChiefBefore = gov.balanceOf(currentContract);
    mathint govBalanceOfOtherBefore = gov.balanceOf(otherAddr2);

    free(e, wad);

    mathint approvalsSlatesVotesSender0After = approvals(slatesVotesSender0);
    mathint approvalsSlatesVotesSender1After = approvals(slatesVotesSender1);
    mathint approvalsSlatesVotesSender2After = approvals(slatesVotesSender2);
    mathint approvalsSlatesVotesSender3After = approvals(slatesVotesSender3);
    mathint approvalsSlatesVotesSender4After = approvals(slatesVotesSender4);
    mathint approvalsSlatesVotesNotSenderAnyAfter = approvals(slatesNotSenderAny);
    mathint depositsSenderAfter = deposits(e.msg.sender);
    mathint depositsOtherAfter = deposits(otherAddr);
    mathint govBalanceOfSenderAfter = gov.balanceOf(e.msg.sender);
    mathint govBalanceOfChiefAfter = gov.balanceOf(currentContract);
    mathint govBalanceOfOtherAfter = gov.balanceOf(otherAddr2);

    assert lengthVotesSender >= 1 => approvalsSlatesVotesSender0After == approvalsSlatesVotesSender0Before - wad, "Assert 1";
    assert lengthVotesSender >= 2 => approvalsSlatesVotesSender1After == approvalsSlatesVotesSender1Before - wad, "Assert 2";
    assert lengthVotesSender >= 3 => approvalsSlatesVotesSender2After == approvalsSlatesVotesSender2Before - wad, "Assert 3";
    assert lengthVotesSender >= 4 => approvalsSlatesVotesSender3After == approvalsSlatesVotesSender3Before - wad, "Assert 4";
    assert lengthVotesSender == 5 => approvalsSlatesVotesSender4After == approvalsSlatesVotesSender4Before - wad, "Assert 5";
    assert approvalsSlatesVotesNotSenderAnyAfter == approvalsSlatesVotesNotSenderAnyBefore, "Assert 6";
    assert depositsSenderAfter == depositsSenderBefore - wad, "Assert 7";
    assert depositsOtherAfter == depositsOtherBefore, "Assert 8";
    assert govBalanceOfSenderAfter == govBalanceOfSenderBefore + wad, "Assert 9";
    assert govBalanceOfChiefAfter == govBalanceOfChiefBefore - wad, "Assert 10";
    assert govBalanceOfOtherAfter == govBalanceOfOtherBefore, "Assert 11";
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
    mathint last = last();

    free@withrevert(e, wad);

    bool revert1 = e.msg.value > 0;
    bool revert2 = e.block.number <= last;
    bool revert3 = depositsSender < to_mathint(wad);
    bool revert4 = lengthVotesSender >= 1 && approvalsSlatesVotesSender0 < to_mathint(wad);
    bool revert5 = lengthVotesSender >= 2 && approvalsSlatesVotesSender1 < to_mathint(wad);
    bool revert6 = lengthVotesSender >= 3 && approvalsSlatesVotesSender2 < to_mathint(wad);
    bool revert7 = lengthVotesSender >= 4 && approvalsSlatesVotesSender3 < to_mathint(wad);
    bool revert8 = lengthVotesSender == 5 && approvalsSlatesVotesSender4 < to_mathint(wad);

    assert lastReverted <=> revert1 || revert2 || revert3 ||
                            revert4 || revert5 || revert6 ||
                            revert7 || revert8, "Revert rules failed";
}

// Verify correct storage changes for non reverting etch
rule etch(address[] yays) {
    env e;

    require yays.length <= 20; // loop_iter limit but >>> maxYays

    mathint maxYays = maxYays();
    require maxYays == 5;

    uint256 anyUint256;
    address anyAddr;

    mathint yaysLength = yays.length;
    bytes32 slateYays = yaysLength <= maxYays ? aux.hashYays(yays) : to_bytes32(0); // To avoid an error on something that won't be used
    bytes32 otherBytes32;
    require otherBytes32 != slateYays;
    require to_mathint(length(slateYays)) <= maxYays; // Not possible to have an existing array larger than maxYays, but still needed for the prover

    address slatesOtherAnyBefore = slates(otherBytes32, anyUint256);

    etch(e, yays);

    mathint slatesSlateYaysLength = length(slateYays);
    address slatesSlateYays0 = yaysLength >= 1 ? slates(slateYays, 0) : 0; // Just any addr as it doesn't save it
    address slatesSlateYays1 = yaysLength >= 2 ? slates(slateYays, 1) : 0;
    address slatesSlateYays2 = yaysLength >= 3 ? slates(slateYays, 2) : 0;
    address slatesSlateYays3 = yaysLength >= 4 ? slates(slateYays, 3) : 0;
    address slatesSlateYays4 = yaysLength == 5 ? slates(slateYays, 4) : 0;
    address slatesOtherAnyAfter = slates(otherBytes32, anyUint256);

    assert slatesSlateYaysLength == yaysLength, "Assert 1";
    assert yaysLength >= 1 => slatesSlateYays0 == yays[0], "Assert 2";
    assert yaysLength >= 2 => slatesSlateYays1 == yays[1], "Assert 3";
    assert yaysLength >= 3 => slatesSlateYays2 == yays[2], "Assert 4";
    assert yaysLength >= 4 => slatesSlateYays3 == yays[3], "Assert 5";
    assert yaysLength == 5 => slatesSlateYays4 == yays[4], "Assert 6";
    assert slatesOtherAnyAfter == slatesOtherAnyBefore, "Assert 7";
}

// Verify revert rules on etch
rule etch_revert(address[] yays) {
    env e;

    require yays.length <= 20; // loop_iter limit but >>> maxYays

    mathint maxYays = maxYays();
    require maxYays == 5;

    mathint yaysLength = yays.length;
    bytes32 slateYays = yaysLength <= maxYays ? aux.hashYays(yays) : to_bytes32(0); // To avoid an error on something that won't be used
    require to_mathint(length(slateYays)) <= maxYays; // Not possible to have an existing array larger than maxYays, but still needed for the prover

    etch@withrevert(e, yays);

    bool revert1 = e.msg.value > 0;
    bool revert2 = yaysLength > maxYays;
    bool revert3 = yaysLength >= 2 && yays[0] >= yays[1];
    bool revert4 = yaysLength >= 3 && yays[1] >= yays[2];
    bool revert5 = yaysLength >= 4 && yays[2] >= yays[3];
    bool revert6 = yaysLength == 5 && yays[3] >= yays[4];

    assert lastReverted <=> revert1 || revert2 || revert3 ||
                            revert4 || revert5 || revert6, "Revert rules failed";
}

// Verify correct storage changes for non reverting vote
rule vote_yays(address[] yays) {
    env e;

    require yays.length <= 20; // loop_iter limit but >>> maxYays

    mathint maxYays = maxYays();
    require maxYays == 5;

    bytes32 anyBytes32;
    uint256 anyUint256;
    address anyAddr;

    mathint yaysLength = to_mathint(yays.length);
    bytes32 slateYays = yaysLength <= maxYays ? aux.hashYays(yays) : to_bytes32(0); // To avoid an error on something that won't be used
    bytes32 otherBytes32;
    require otherBytes32 != slateYays;
    require to_mathint(length(slateYays)) <= maxYays; // Not possible to have an existing array larger than maxYays, but still needed for the prover

    address otherAddr;
    require otherAddr != e.msg.sender;

    address slatesOtherAnyBefore = slates(otherBytes32, anyUint256);
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
    require lengthVotesSender == yaysLength && yaysLength >= 1 &&
            slatesVotesSender0 != yays[0]
            => votesSenderBefore != slateYays;
    require lengthVotesSender == yaysLength && yaysLength >= 2 &&
            slatesVotesSender1 != yays[1]
            => votesSenderBefore != slateYays;
    require lengthVotesSender == yaysLength && yaysLength >= 3 &&
            slatesVotesSender2 != yays[2]
            => votesSenderBefore != slateYays;
    require lengthVotesSender == yaysLength && yaysLength >= 4 &&
            slatesVotesSender3 != yays[3]
            => votesSenderBefore != slateYays;
    require lengthVotesSender == yaysLength && yaysLength == 5 &&
            slatesVotesSender4 != yays[4]
            => votesSenderBefore != slateYays;
    //

    require lengthVotesSender <= 1 || slatesVotesSender1 > slatesVotesSender0;
    require lengthVotesSender <= 2 || slatesVotesSender2 > slatesVotesSender1;
    require lengthVotesSender <= 3 || slatesVotesSender3 > slatesVotesSender2;
    require lengthVotesSender <= 4 || slatesVotesSender4 > slatesVotesSender3;
    require yaysLength <= 1 || yays[1] > yays[0];
    require yaysLength <= 2 || yays[2] > yays[1];
    require yaysLength <= 3 || yays[3] > yays[2];
    require yaysLength <= 4 || yays[4] > yays[3];
    address slatesOtherAny;
    require (lengthVotesSender < 1 || slatesOtherAny != slatesVotesSender0) &&
            (lengthVotesSender < 2 || slatesOtherAny != slatesVotesSender1) &&
            (lengthVotesSender < 3 || slatesOtherAny != slatesVotesSender2) &&
            (lengthVotesSender < 4 || slatesOtherAny != slatesVotesSender3) &&
            (lengthVotesSender < 5 || slatesOtherAny != slatesVotesSender4);
    require (yaysLength < 1 || slatesOtherAny != yays[0]) &&
            (yaysLength < 2 || slatesOtherAny != yays[1]) &&
            (yaysLength < 3 || slatesOtherAny != yays[2]) &&
            (yaysLength < 4 || slatesOtherAny != yays[3]) &&
            (yaysLength < 5 || slatesOtherAny != yays[4]);
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

    vote(e, yays);

    mathint lengthSlateYays = length(slateYays);
    address slatesSlateYays0 = yaysLength >= 1 ? slates(slateYays, 0) : addr0; // Just any addr as it doesn't save it
    address slatesSlateYays1 = yaysLength >= 2 ? slates(slateYays, 1) : addr0;
    address slatesSlateYays2 = yaysLength >= 3 ? slates(slateYays, 2) : addr0;
    address slatesSlateYays3 = yaysLength >= 4 ? slates(slateYays, 3) : addr0;
    address slatesSlateYays4 = yaysLength == 5 ? slates(slateYays, 4) : addr0;
    address slatesOtherAnyAfter = slates(otherBytes32, anyUint256);
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
    mathint depositsSender = deposits(e.msg.sender);

    assert lengthSlateYays == yaysLength, "Assert 1";
    assert yaysLength >= 1 => slatesSlateYays0 == yays[0], "Assert 2";
    assert yaysLength >= 2 => slatesSlateYays1 == yays[1], "Assert 3";
    assert yaysLength >= 3 => slatesSlateYays2 == yays[2], "Assert 4";
    assert yaysLength >= 4 => slatesSlateYays3 == yays[3], "Assert 5";
    assert yaysLength == 5 => slatesSlateYays4 == yays[4], "Assert 6";
    assert slatesOtherAnyAfter == slatesOtherAnyBefore, "Assert 7";
    assert votesSenderAfter == slateYays, "Assert 8";
    assert votesOtherAfter == votesOtherBefore, "Assert 9";
    bool notInYays0 =   (yaysLength < 1 || slatesVotesSender0 != yays[0]) &&
                        (yaysLength < 2 || slatesVotesSender0 != yays[1]) &&
                        (yaysLength < 3 || slatesVotesSender0 != yays[2]) &&
                        (yaysLength < 4 || slatesVotesSender0 != yays[3]) &&
                        (yaysLength < 5 || slatesVotesSender0 != yays[4]);
    assert lengthVotesSender >= 1 &&  notInYays0 => approvalsSlatesVotesSender0After == approvalsSlatesVotesSender0Before - depositsSender, "Assert 10";
    assert lengthVotesSender >= 1 && !notInYays0 => approvalsSlatesVotesSender0After == approvalsSlatesVotesSender0Before,                  "Assert 11";
    bool notInYays1 =   (yaysLength < 1 || slatesVotesSender1 != yays[0]) &&
                        (yaysLength < 2 || slatesVotesSender1 != yays[1]) &&
                        (yaysLength < 3 || slatesVotesSender1 != yays[2]) &&
                        (yaysLength < 4 || slatesVotesSender1 != yays[3]) &&
                        (yaysLength < 5 || slatesVotesSender1 != yays[4]);
    assert lengthVotesSender >= 2 &&  notInYays1 => approvalsSlatesVotesSender1After == approvalsSlatesVotesSender1Before - depositsSender, "Assert 12";
    assert lengthVotesSender >= 2 && !notInYays1 => approvalsSlatesVotesSender1After == approvalsSlatesVotesSender1Before,                  "Assert 13";
    bool notInYays2 =   (yaysLength < 1 || slatesVotesSender2 != yays[0]) &&
                        (yaysLength < 2 || slatesVotesSender2 != yays[1]) &&
                        (yaysLength < 3 || slatesVotesSender2 != yays[2]) &&
                        (yaysLength < 4 || slatesVotesSender2 != yays[3]) &&
                        (yaysLength < 5 || slatesVotesSender2 != yays[4]);
    assert lengthVotesSender >= 3 &&  notInYays2 => approvalsSlatesVotesSender2After == approvalsSlatesVotesSender2Before - depositsSender, "Assert 14";
    assert lengthVotesSender >= 3 && !notInYays2 => approvalsSlatesVotesSender2After == approvalsSlatesVotesSender2Before,                  "Assert 15";
    bool notInYays3 =   (yaysLength < 1 || slatesVotesSender3 != yays[0]) &&
                        (yaysLength < 2 || slatesVotesSender3 != yays[1]) &&
                        (yaysLength < 3 || slatesVotesSender3 != yays[2]) &&
                        (yaysLength < 4 || slatesVotesSender3 != yays[3]) &&
                        (yaysLength < 5 || slatesVotesSender3 != yays[4]);
    assert lengthVotesSender >= 4 &&  notInYays3 => approvalsSlatesVotesSender3After == approvalsSlatesVotesSender3Before - depositsSender, "Assert 16";
    assert lengthVotesSender >= 4 && !notInYays3 => approvalsSlatesVotesSender3After == approvalsSlatesVotesSender3Before,                  "Assert 17";
    bool notInYays4 =   (yaysLength < 1 || slatesVotesSender4 != yays[0]) &&
                        (yaysLength < 2 || slatesVotesSender4 != yays[1]) &&
                        (yaysLength < 3 || slatesVotesSender4 != yays[2]) &&
                        (yaysLength < 4 || slatesVotesSender4 != yays[3]) &&
                        (yaysLength < 5 || slatesVotesSender4 != yays[4]);
    assert lengthVotesSender == 5 &&  notInYays4 => approvalsSlatesVotesSender4After == approvalsSlatesVotesSender4Before - depositsSender, "Assert 18";
    assert lengthVotesSender == 5 && !notInYays4 => approvalsSlatesVotesSender4After == approvalsSlatesVotesSender4Before,                  "Assert 19";
    assert yaysLength >= 1 &&
           (lengthVotesSender < 1 || yays[0] != slatesVotesSender0) &&
           (lengthVotesSender < 2 || yays[0] != slatesVotesSender1) &&
           (lengthVotesSender < 3 || yays[0] != slatesVotesSender2) &&
           (lengthVotesSender < 4 || yays[0] != slatesVotesSender3) &&
           (lengthVotesSender < 5 || yays[0] != slatesVotesSender4)
           => approvalsYays0After == approvalsYays0Before + depositsSender, "Assert 20";
    assert yaysLength >= 2 &&
           (lengthVotesSender < 1 || yays[1] != slatesVotesSender0) &&
           (lengthVotesSender < 2 || yays[1] != slatesVotesSender1) &&
           (lengthVotesSender < 3 || yays[1] != slatesVotesSender2) &&
           (lengthVotesSender < 4 || yays[1] != slatesVotesSender3) &&
           (lengthVotesSender < 5 || yays[1] != slatesVotesSender4)
           => approvalsYays1After == approvalsYays1Before + depositsSender, "Assert 21";
    assert yaysLength >= 3 &&
           (lengthVotesSender < 1 || yays[2] != slatesVotesSender0) &&
           (lengthVotesSender < 2 || yays[2] != slatesVotesSender1) &&
           (lengthVotesSender < 3 || yays[2] != slatesVotesSender2) &&
           (lengthVotesSender < 4 || yays[2] != slatesVotesSender3) &&
           (lengthVotesSender < 5 || yays[2] != slatesVotesSender4)
           => approvalsYays2After == approvalsYays2Before + depositsSender, "Assert 22";
    assert yaysLength >= 4 &&
           (lengthVotesSender < 1 || yays[3] != slatesVotesSender0) &&
           (lengthVotesSender < 2 || yays[3] != slatesVotesSender1) &&
           (lengthVotesSender < 3 || yays[3] != slatesVotesSender2) &&
           (lengthVotesSender < 4 || yays[3] != slatesVotesSender3) &&
           (lengthVotesSender < 5 || yays[3] != slatesVotesSender4)
           => approvalsYays3After == approvalsYays3Before + depositsSender, "Assert 23";
    assert yaysLength == 5 &&
           (lengthVotesSender < 1 || yays[4] != slatesVotesSender0) &&
           (lengthVotesSender < 2 || yays[4] != slatesVotesSender1) &&
           (lengthVotesSender < 3 || yays[4] != slatesVotesSender2) &&
           (lengthVotesSender < 4 || yays[4] != slatesVotesSender3) &&
           (lengthVotesSender < 5 || yays[4] != slatesVotesSender4)
           => approvalsYays4After == approvalsYays4Before + depositsSender, "Assert 24";
    assert approvalsYaysNotSenderAfter == approvalsYaysNotSenderBefore, "Assert 25";
}

// Verify revert rules on vote
rule vote_yays_revert(address[] yays) {
    env e;

    require yays.length <= 20; // loop_iter limit but >>> maxYays

    mathint maxYays = maxYays();
    require maxYays == 5;

    bytes32 EMPTY_SLATE = EMPTY_SLATE();

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
    require lengthVotesSender == yaysLength && yaysLength >= 1 &&
            slatesVotesSender0 != yays[0]
            => votesSender != slateYays;
    require lengthVotesSender == yaysLength && yaysLength >= 2 &&
            slatesVotesSender1 != yays[1]
            => votesSender != slateYays;
    require lengthVotesSender == yaysLength && yaysLength >= 3 &&
            slatesVotesSender2 != yays[2]
            => votesSender != slateYays;
    require lengthVotesSender == yaysLength && yaysLength >= 4 &&
            slatesVotesSender3 != yays[3]
            => votesSender != slateYays;
    require lengthVotesSender == yaysLength && yaysLength == 5 &&
            slatesVotesSender4 != yays[4]
            => votesSender != slateYays;

    vote@withrevert(e, yays);

    bool revert1  = e.msg.value > 0;
    bool revert2  = yaysLength > maxYays;
    bool revert3  = yaysLength >= 2 && yays[0] >= yays[1];
    bool revert4  = yaysLength >= 3 && yays[1] >= yays[2];
    bool revert5  = yaysLength >= 4 && yays[2] >= yays[3];
    bool revert6  = yaysLength == 5 && yays[3] >= yays[4];
    bool revert7  = yaysLength == 0 && slateYays != EMPTY_SLATE;
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

    assert lastReverted <=> revert1  || revert2  || revert3  ||
                            revert4  || revert5  || revert6  ||
                            revert7  || revert8  || revert9  ||
                            revert10 || revert11 || revert12 ||
                            revert13 || revert14 || revert15 ||
                            revert16 || revert17, "Revert rules failed";
}

// Verify correct storage changes for non reverting vote
rule vote_slate(bytes32 slate) {
    env e;

    mathint maxYays = maxYays();
    require maxYays == 5;

    address otherAddr;
    require otherAddr != e.msg.sender;

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

    vote(e, slate);

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

    assert votesSenderAfter == slate, "Assert 1";
    assert votesOtherAfter == votesOtherBefore, "Assert 2";
    bool notInSlate0 =  (lengthSlate < 1 || slatesVotesSender0 != slatesSlate0) &&
                        (lengthSlate < 2 || slatesVotesSender0 != slatesSlate1) &&
                        (lengthSlate < 3 || slatesVotesSender0 != slatesSlate2) &&
                        (lengthSlate < 4 || slatesVotesSender0 != slatesSlate3) &&
                        (lengthSlate < 5 || slatesVotesSender0 != slatesSlate4);
    assert lengthVotesSender >= 1 &&  notInSlate0 => approvalsSlatesVotesSender0After == approvalsSlatesVotesSender0Before - depositsSender, "Assert 3";
    assert lengthVotesSender >= 1 && !notInSlate0 => approvalsSlatesVotesSender0After == approvalsSlatesVotesSender0Before,                  "Assert 4";
    bool notInSlate1 =  (lengthSlate < 1 || slatesVotesSender1 != slatesSlate0) &&
                        (lengthSlate < 2 || slatesVotesSender1 != slatesSlate1) &&
                        (lengthSlate < 3 || slatesVotesSender1 != slatesSlate2) &&
                        (lengthSlate < 4 || slatesVotesSender1 != slatesSlate3) &&
                        (lengthSlate < 5 || slatesVotesSender1 != slatesSlate4);
    assert lengthVotesSender >= 2 &&  notInSlate1 => approvalsSlatesVotesSender1After == approvalsSlatesVotesSender1Before - depositsSender, "Assert 5";
    assert lengthVotesSender >= 2 && !notInSlate1 => approvalsSlatesVotesSender1After == approvalsSlatesVotesSender1Before,                  "Assert 6";
    bool notInSlate2 =  (lengthSlate < 1 || slatesVotesSender2 != slatesSlate0) &&
                        (lengthSlate < 2 || slatesVotesSender2 != slatesSlate1) &&
                        (lengthSlate < 3 || slatesVotesSender2 != slatesSlate2) &&
                        (lengthSlate < 4 || slatesVotesSender2 != slatesSlate3) &&
                        (lengthSlate < 5 || slatesVotesSender2 != slatesSlate4);
    assert lengthVotesSender >= 3 &&  notInSlate2 => approvalsSlatesVotesSender2After == approvalsSlatesVotesSender2Before - depositsSender, "Assert 7";
    assert lengthVotesSender >= 3 && !notInSlate2 => approvalsSlatesVotesSender2After == approvalsSlatesVotesSender2Before,                  "Assert 8";
    bool notInSlate3 =  (lengthSlate < 1 || slatesVotesSender3 != slatesSlate0) &&
                        (lengthSlate < 2 || slatesVotesSender3 != slatesSlate1) &&
                        (lengthSlate < 3 || slatesVotesSender3 != slatesSlate2) &&
                        (lengthSlate < 4 || slatesVotesSender3 != slatesSlate3) &&
                        (lengthSlate < 5 || slatesVotesSender3 != slatesSlate4);
    assert lengthVotesSender >= 4 &&  notInSlate3 => approvalsSlatesVotesSender3After == approvalsSlatesVotesSender3Before - depositsSender, "Assert 9";
    assert lengthVotesSender >= 4 && !notInSlate3 => approvalsSlatesVotesSender3After == approvalsSlatesVotesSender3Before,                  "Assert 10";
    bool notInSlate4 =  (lengthSlate < 1 || slatesVotesSender4 != slatesSlate0) &&
                        (lengthSlate < 2 || slatesVotesSender4 != slatesSlate1) &&
                        (lengthSlate < 3 || slatesVotesSender4 != slatesSlate2) &&
                        (lengthSlate < 4 || slatesVotesSender4 != slatesSlate3) &&
                        (lengthSlate < 5 || slatesVotesSender4 != slatesSlate4);
    assert lengthVotesSender == 5 &&  notInSlate4 => approvalsSlatesVotesSender4After == approvalsSlatesVotesSender4Before - depositsSender, "Assert 11";
    assert lengthVotesSender == 5 && !notInSlate4 => approvalsSlatesVotesSender4After == approvalsSlatesVotesSender4Before,                  "Assert 12";
    assert lengthSlate >= 1 &&
           (lengthVotesSender < 1 || slatesSlate0 != slatesVotesSender0) &&
           (lengthVotesSender < 2 || slatesSlate0 != slatesVotesSender1) &&
           (lengthVotesSender < 3 || slatesSlate0 != slatesVotesSender2) &&
           (lengthVotesSender < 4 || slatesSlate0 != slatesVotesSender3) &&
           (lengthVotesSender < 5 || slatesSlate0 != slatesVotesSender4)
           => approvalsSlatesSlate0After == approvalsSlatesSlate0Before + depositsSender, "Assert 13";
    assert lengthSlate >= 2 &&
           (lengthVotesSender < 1 || slatesSlate1 != slatesVotesSender0) &&
           (lengthVotesSender < 2 || slatesSlate1 != slatesVotesSender1) &&
           (lengthVotesSender < 3 || slatesSlate1 != slatesVotesSender2) &&
           (lengthVotesSender < 4 || slatesSlate1 != slatesVotesSender3) &&
           (lengthVotesSender < 5 || slatesSlate1 != slatesVotesSender4)
           => approvalsSlatesSlate1After == approvalsSlatesSlate1Before + depositsSender, "Assert 14";
    assert lengthSlate >= 3 &&
           (lengthVotesSender < 1 || slatesSlate2 != slatesVotesSender0) &&
           (lengthVotesSender < 2 || slatesSlate2 != slatesVotesSender1) &&
           (lengthVotesSender < 3 || slatesSlate2 != slatesVotesSender2) &&
           (lengthVotesSender < 4 || slatesSlate2 != slatesVotesSender3) &&
           (lengthVotesSender < 5 || slatesSlate2 != slatesVotesSender4)
           => approvalsSlatesSlate2After == approvalsSlatesSlate2Before + depositsSender, "Assert 15";
    assert lengthSlate >= 4 &&
           (lengthVotesSender < 1 || slatesSlate3 != slatesVotesSender0) &&
           (lengthVotesSender < 2 || slatesSlate3 != slatesVotesSender1) &&
           (lengthVotesSender < 3 || slatesSlate3 != slatesVotesSender2) &&
           (lengthVotesSender < 4 || slatesSlate3 != slatesVotesSender3) &&
           (lengthVotesSender < 5 || slatesSlate3 != slatesVotesSender4)
           => approvalsSlatesSlate3After == approvalsSlatesSlate3Before + depositsSender, "Assert 16";
    assert lengthSlate == 5 &&
           (lengthVotesSender < 1 || slatesSlate4 != slatesVotesSender0) &&
           (lengthVotesSender < 2 || slatesSlate4 != slatesVotesSender1) &&
           (lengthVotesSender < 3 || slatesSlate4 != slatesVotesSender2) &&
           (lengthVotesSender < 4 || slatesSlate4 != slatesVotesSender3) &&
           (lengthVotesSender < 5 || slatesSlate4 != slatesVotesSender4)
           => approvalsSlatesSlate4After == approvalsSlatesSlate4Before + depositsSender, "Assert 17";
    assert approvalsSlatesOtherAnyAfter == approvalsSlatesOtherAnyBefore, "Assert 18";
}

// Verify revert rules on vote
rule vote_slate_revert(bytes32 slate) {
    env e;

    mathint maxYays = maxYays();
    require maxYays == 5;

    bytes32 EMPTY_SLATE = EMPTY_SLATE();

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

    vote@withrevert(e, slate);

    bool revert1  = e.msg.value > 0;
    bool revert2  = lengthSlate == 0 && slate != EMPTY_SLATE;
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

    assert lastReverted <=> revert1  || revert2  || revert3 ||
                            revert4  || revert5  || revert6 ||
                            revert7  || revert8  || revert9 ||
                            revert10 || revert11 || revert12, "Revert rules failed";
}

// Verify correct storage changes for non reverting lift
rule lift(address whom) {
    env e;

    lift(e, whom);

    address hatAfter = hat();
    mathint lastAfter = last();

    assert hatAfter == whom, "Assert 1";
    assert lastAfter == e.block.number, "Assert 2";
}

// Verify revert rules on lift
rule lift_revert(address whom) {
    env e;

    address hat = hat();
    mathint approvalsWhom = approvals(whom);
    mathint approvalsHat = approvals(hat);
    mathint last = last();
    mathint liftCooldown = liftCooldown();

    lift@withrevert(e, whom);

    bool revert1 = e.msg.value > 0;
    bool revert2 = e.block.number != last && e.block.number <= last + liftCooldown;
    bool revert3 = approvalsWhom <= approvalsHat;

    assert lastReverted <=> revert1 || revert2 || revert3, "Revert rules failed";
}
