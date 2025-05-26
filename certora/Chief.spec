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
    mathint votesSenderLength = length(votesSender);
    require votesSenderLength <= maxYays;
    address[] slatesVotesSender;
    require slatesVotesSender[0] == slates(votesSender, 0);
    require slatesVotesSender[1] == slates(votesSender, 1);
    require slatesVotesSender[2] == slates(votesSender, 2);
    require slatesVotesSender[3] == slates(votesSender, 3);
    require slatesVotesSender[4] == slates(votesSender, 4);
    require votesSenderLength <= 1 || (forall uint256 i. forall uint256 j. to_mathint(j) == i + 1 && j < votesSenderLength => slatesVotesSender[j] > slatesVotesSender[i]);
    address slatesNotSenderAny;
    require forall uint256 i. i < votesSenderLength => slatesVotesSender[i] != slatesNotSenderAny;
    uint256[] approvalsSlatesSenderBefore;
    require approvalsSlatesSenderBefore[0] == approvals(slatesVotesSender[0]);
    require approvalsSlatesSenderBefore[1] == approvals(slatesVotesSender[1]);
    require approvalsSlatesSenderBefore[2] == approvals(slatesVotesSender[2]);
    require approvalsSlatesSenderBefore[3] == approvals(slatesVotesSender[3]);
    require approvalsSlatesSenderBefore[4] == approvals(slatesVotesSender[4]);
    mathint approvalsSlatesNotSenderAnyBefore = approvals(slatesNotSenderAny);
    mathint depositsSenderBefore = deposits(e.msg.sender);
    mathint depositsOtherBefore = deposits(otherAddr);
    mathint govBalanceOfSenderBefore = gov.balanceOf(e.msg.sender);
    mathint govBalanceOfChiefBefore = gov.balanceOf(currentContract);
    mathint govBalanceOfOtherBefore = gov.balanceOf(otherAddr2);

    lock(e, wad);

    uint256[] approvalsSlatesSenderAfter;
    require approvalsSlatesSenderAfter[0] == approvals(slatesVotesSender[0]);
    require approvalsSlatesSenderAfter[1] == approvals(slatesVotesSender[1]);
    require approvalsSlatesSenderAfter[2] == approvals(slatesVotesSender[2]);
    require approvalsSlatesSenderAfter[3] == approvals(slatesVotesSender[3]);
    require approvalsSlatesSenderAfter[4] == approvals(slatesVotesSender[4]);
    mathint approvalsSlatesNotSenderAnyAfter = approvals(slatesNotSenderAny);
    mathint depositsSenderAfter = deposits(e.msg.sender);
    mathint depositsOtherAfter = deposits(otherAddr);
    mathint govBalanceOfSenderAfter = gov.balanceOf(e.msg.sender);
    mathint govBalanceOfChiefAfter = gov.balanceOf(currentContract);
    mathint govBalanceOfOtherAfter = gov.balanceOf(otherAddr2);

    assert forall uint256 i. i < votesSenderLength => approvalsSlatesSenderAfter[i] == approvalsSlatesSenderBefore[i] + wad, "Assert 1";
    assert approvalsSlatesNotSenderAnyAfter == approvalsSlatesNotSenderAnyBefore, "Assert 2";
    assert depositsSenderAfter == depositsSenderBefore + wad, "Assert 3";
    assert depositsOtherAfter == depositsOtherBefore, "Assert 4";
    assert govBalanceOfSenderAfter == govBalanceOfSenderBefore - wad, "Assert 5";
    assert govBalanceOfChiefAfter == govBalanceOfChiefBefore + wad, "Assert 6";
    assert govBalanceOfOtherAfter == govBalanceOfOtherBefore, "Assert 7";
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
    mathint votesSenderLength = length(votesSender);
    require votesSenderLength <= maxYays;
    address[] slatesVotesSender;
    require slatesVotesSender[0] == slates(votesSender, 0);
    require slatesVotesSender[1] == slates(votesSender, 1);
    require slatesVotesSender[2] == slates(votesSender, 2);
    require slatesVotesSender[3] == slates(votesSender, 3);
    require slatesVotesSender[4] == slates(votesSender, 4);
    require votesSenderLength <= 1 || (forall uint256 i. forall uint256 j. to_mathint(j) == i + 1 && j < votesSenderLength => slatesVotesSender[j] > slatesVotesSender[i]);
    uint256[] approvalsSlatesVotesSender;
    require approvalsSlatesVotesSender[0] == approvals(slatesVotesSender[0]);
    require approvalsSlatesVotesSender[1] == approvals(slatesVotesSender[1]);
    require approvalsSlatesVotesSender[2] == approvals(slatesVotesSender[2]);
    require approvalsSlatesVotesSender[3] == approvals(slatesVotesSender[3]);
    require approvalsSlatesVotesSender[4] == approvals(slatesVotesSender[4]);

    lock@withrevert(e, wad);

    bool revert1 = e.msg.value > 0;
    bool revert2 = depositsSender + wad > max_uint256;
    bool revert3 = exists uint256 i. i < votesSenderLength && approvalsSlatesVotesSender[i] + wad > max_uint256;

    bool reverts = revert1 || revert2 || revert3;
    assert lastReverted => reverts, "Missing revert rules";
    assert reverts => lastReverted, "Revert rules failed";
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
    mathint votesSenderLength = length(votesSender);
    require votesSenderLength <= maxYays;
    address[] slatesVotesSender;
    require slatesVotesSender[0] == slates(votesSender, 0);
    require slatesVotesSender[1] == slates(votesSender, 1);
    require slatesVotesSender[2] == slates(votesSender, 2);
    require slatesVotesSender[3] == slates(votesSender, 3);
    require slatesVotesSender[4] == slates(votesSender, 4);
    require votesSenderLength <= 1 || (forall uint256 i. forall uint256 j. to_mathint(j) == i + 1 && j < votesSenderLength => slatesVotesSender[j] > slatesVotesSender[i]);
    address slatesNotSenderAny;
    require forall uint256 i. i < votesSenderLength => slatesVotesSender[i] != slatesNotSenderAny;
    uint256[] approvalsSlatesSenderBefore;
    require approvalsSlatesSenderBefore[0] == approvals(slatesVotesSender[0]);
    require approvalsSlatesSenderBefore[1] == approvals(slatesVotesSender[1]);
    require approvalsSlatesSenderBefore[2] == approvals(slatesVotesSender[2]);
    require approvalsSlatesSenderBefore[3] == approvals(slatesVotesSender[3]);
    require approvalsSlatesSenderBefore[4] == approvals(slatesVotesSender[4]);
    mathint approvalsSlatesNotSenderAnyBefore = approvals(slatesNotSenderAny);
    mathint depositsSenderBefore = deposits(e.msg.sender);
    mathint depositsOtherBefore = deposits(otherAddr);
    mathint govBalanceOfSenderBefore = gov.balanceOf(e.msg.sender);
    mathint govBalanceOfChiefBefore = gov.balanceOf(currentContract);
    mathint govBalanceOfOtherBefore = gov.balanceOf(otherAddr2);

    free(e, wad);

    uint256[] approvalsSlatesSenderAfter;
    require approvalsSlatesSenderAfter[0] == approvals(slatesVotesSender[0]);
    require approvalsSlatesSenderAfter[1] == approvals(slatesVotesSender[1]);
    require approvalsSlatesSenderAfter[2] == approvals(slatesVotesSender[2]);
    require approvalsSlatesSenderAfter[3] == approvals(slatesVotesSender[3]);
    require approvalsSlatesSenderAfter[4] == approvals(slatesVotesSender[4]);
    mathint approvalsSlatesNotSenderAnyAfter = approvals(slatesNotSenderAny);
    mathint depositsSenderAfter = deposits(e.msg.sender);
    mathint depositsOtherAfter = deposits(otherAddr);
    mathint govBalanceOfSenderAfter = gov.balanceOf(e.msg.sender);
    mathint govBalanceOfChiefAfter = gov.balanceOf(currentContract);
    mathint govBalanceOfOtherAfter = gov.balanceOf(otherAddr2);

    assert forall uint256 i. i < votesSenderLength => approvalsSlatesSenderAfter[i] == approvalsSlatesSenderBefore[i] - wad, "Assert 1";
    assert approvalsSlatesNotSenderAnyAfter == approvalsSlatesNotSenderAnyBefore, "Assert 2";
    assert depositsSenderAfter == depositsSenderBefore - wad, "Assert 3";
    assert depositsOtherAfter == depositsOtherBefore, "Assert 4";
    assert govBalanceOfSenderAfter == govBalanceOfSenderBefore + wad, "Assert 5";
    assert govBalanceOfChiefAfter == govBalanceOfChiefBefore - wad, "Assert 6";
    assert govBalanceOfOtherAfter == govBalanceOfOtherBefore, "Assert 7";
}

// Verify revert rules on free
rule free_revert(uint256 wad) {
    env e;

    mathint maxYays = maxYays();
    require maxYays == 5;
    require gov.balanceOf(currentContract) >= wad;
    require gov.balanceOf(e.msg.sender) + wad < max_uint256;
    require e.msg.sender != 0 && e.msg.sender != gov;

    mathint depositsSender = deposits(e.msg.sender);
    bytes32 votesSender = votes(e.msg.sender);
    mathint votesSenderLength = length(votesSender);
    require votesSenderLength <= maxYays;
    address[] slatesVotesSender;
    require slatesVotesSender[0] == slates(votesSender, 0);
    require slatesVotesSender[1] == slates(votesSender, 1);
    require slatesVotesSender[2] == slates(votesSender, 2);
    require slatesVotesSender[3] == slates(votesSender, 3);
    require slatesVotesSender[4] == slates(votesSender, 4);
    require votesSenderLength <= 1 || (forall uint256 i. forall uint256 j. to_mathint(j) == i + 1 && j < votesSenderLength => slatesVotesSender[j] > slatesVotesSender[i]);
    uint256[] approvalsSlatesVotesSender;
    require approvalsSlatesVotesSender[0] == approvals(slatesVotesSender[0]);
    require approvalsSlatesVotesSender[1] == approvals(slatesVotesSender[1]);
    require approvalsSlatesVotesSender[2] == approvals(slatesVotesSender[2]);
    require approvalsSlatesVotesSender[3] == approvals(slatesVotesSender[3]);
    require approvalsSlatesVotesSender[4] == approvals(slatesVotesSender[4]);
    mathint last = last();

    free@withrevert(e, wad);

    bool revert1 = e.msg.value > 0;
    bool revert2 = e.block.number <= last;
    bool revert3 = depositsSender < to_mathint(wad);
    bool revert4 = exists uint256 i. i < votesSenderLength && approvalsSlatesVotesSender[i] < wad;

    bool reverts = revert1 || revert2 || revert3 || revert4;
    assert lastReverted => reverts, "Missing revert rules";
    assert reverts => lastReverted, "Revert rules failed";
}

// Verify correct storage changes for non reverting etch
rule etch(address[] yays) {
    env e;

    mathint yaysLength = yays.length;
    require yaysLength <= 20; // loop_iter limit but >>> maxYays

    mathint maxYays = maxYays();
    require maxYays == 5;

    uint256 anyUint256;

    bytes32 slateYays = yaysLength <= maxYays ? aux.hashYays(yays) : to_bytes32(0); // To avoid an error on something that won't be used
    bytes32 otherBytes32;
    require otherBytes32 != slateYays;
    require to_mathint(length(slateYays)) <= maxYays; // Not possible to have an existing array larger than maxYays, but still needed for the prover

    address slatesOtherAnyBefore = slates(otherBytes32, anyUint256);

    etch(e, yays);

    mathint slatesSlateYaysLength = length(slateYays);
    address[] slatesSlateYays;
    require slatesSlateYays[0] == slates(slateYays, 0);
    require slatesSlateYays[1] == slates(slateYays, 1);
    require slatesSlateYays[2] == slates(slateYays, 2);
    require slatesSlateYays[3] == slates(slateYays, 3);
    require slatesSlateYays[4] == slates(slateYays, 4);
    address slatesOtherAnyAfter = slates(otherBytes32, anyUint256);

    assert slatesSlateYaysLength == yaysLength, "Assert 1";
    assert forall uint256 i. i < slatesSlateYaysLength => slatesSlateYays[i] == yays[i], "Assert 2";
    assert slatesOtherAnyAfter == slatesOtherAnyBefore, "Assert 3";
}

// Verify revert rules on etch
rule etch_revert(address[] yays) {
    env e;

    mathint yaysLength = yays.length;
    require yaysLength <= 20; // loop_iter limit but >>> maxYays

    mathint maxYays = maxYays();
    require maxYays == 5;

    bytes32 slateYays = yaysLength <= maxYays ? aux.hashYays(yays) : to_bytes32(0); // To avoid an error on something that won't be used
    require to_mathint(length(slateYays)) <= maxYays; // Not possible to have an existing array larger than maxYays, but still needed for the prover

    etch@withrevert(e, yays);

    bool revert1 = e.msg.value > 0;
    bool revert2 = yaysLength > maxYays;
    bool revert3 = yaysLength > 1 && (exists uint256 i. exists uint256 j. to_mathint(j) == i + 1 && j < yaysLength && yays[j] <= yays[i]);

    bool reverts = revert1 || revert2 || revert3;
    assert lastReverted => reverts, "Missing revert rules";
    assert reverts => lastReverted, "Revert rules failed";
}

// Verify correct storage changes for non reverting vote
rule vote_yays(address[] yays) {
    env e;

    mathint yaysLength = yays.length;
    require yaysLength <= 20; // loop_iter limit but >>> maxYays

    mathint maxYays = maxYays();
    require maxYays == 5;

    uint256 anyUint256;

    bytes32 slateYays = yaysLength <= maxYays ? aux.hashYays(yays) : to_bytes32(0); // To avoid an error on something that won't be used
    bytes32 otherBytes32;
    require otherBytes32 != slateYays;
    require to_mathint(length(slateYays)) <= maxYays; // Not possible to have an existing array larger than maxYays, but still needed for the prover

    address otherAddr;
    require otherAddr != e.msg.sender;

    address slatesOtherAnyBefore = slates(otherBytes32, anyUint256);
    bytes32 votesSenderBefore = votes(e.msg.sender);
    bytes32 votesOtherBefore = votes(otherAddr);
    mathint votesSenderLength = length(votesSenderBefore);
    require votesSenderLength <= maxYays;
    address[] slatesVotesSender;
    require slatesVotesSender[0] == slates(votesSenderBefore, 0);
    require slatesVotesSender[1] == slates(votesSenderBefore, 1);
    require slatesVotesSender[2] == slates(votesSenderBefore, 2);
    require slatesVotesSender[3] == slates(votesSenderBefore, 3);
    require slatesVotesSender[4] == slates(votesSenderBefore, 4);
    // This is to avoid that the hash of the new voting array can collide with the hash of the prev existing voted (if not the same content)
    require votesSenderLength != yaysLength || (exists uint256 i. i < yaysLength && slatesVotesSender[i] != yays[i]) => votesSenderBefore != slateYays;
    require votesSenderLength <= 1 || (forall uint256 i. forall uint256 j. to_mathint(j) == i + 1 && j < votesSenderLength => slatesVotesSender[j] > slatesVotesSender[i]);
    address slatesOther;
    require forall uint256 i. i < votesSenderLength => slatesOther != slatesVotesSender[i];
    require forall uint256 i. i < yaysLength => slatesOther != yays[i];
    uint256[] approvalsSlatesVotesSenderBefore;
    require approvalsSlatesVotesSenderBefore[0] == approvals(slatesVotesSender[0]);
    require approvalsSlatesVotesSenderBefore[1] == approvals(slatesVotesSender[1]);
    require approvalsSlatesVotesSenderBefore[2] == approvals(slatesVotesSender[2]);
    require approvalsSlatesVotesSenderBefore[3] == approvals(slatesVotesSender[3]);
    require approvalsSlatesVotesSenderBefore[4] == approvals(slatesVotesSender[4]);
    uint256[] approvalsYaysBefore;
    require approvalsYaysBefore[0] == approvals(yays[0]);
    require approvalsYaysBefore[1] == approvals(yays[1]);
    require approvalsYaysBefore[2] == approvals(yays[2]);
    require approvalsYaysBefore[3] == approvals(yays[3]);
    require approvalsYaysBefore[4] == approvals(yays[4]);
    mathint approvalsSlatesOtherBefore = approvals(slatesOther);

    vote(e, yays);

    mathint slateYaysLength = length(slateYays);
    address[] slatesSlateYays;
    require slatesSlateYays[0] == slates(slateYays, 0);
    require slatesSlateYays[1] == slates(slateYays, 1);
    require slatesSlateYays[2] == slates(slateYays, 2);
    require slatesSlateYays[3] == slates(slateYays, 3);
    require slatesSlateYays[4] == slates(slateYays, 4);
    address slatesOtherAnyAfter = slates(otherBytes32, anyUint256);
    bytes32 votesSenderAfter = votes(e.msg.sender);
    bytes32 votesOtherAfter = votes(otherAddr);
    uint256[] approvalsSlatesVotesSenderAfter;
    require approvalsSlatesVotesSenderAfter[0] == approvals(slatesVotesSender[0]);
    require approvalsSlatesVotesSenderAfter[1] == approvals(slatesVotesSender[1]);
    require approvalsSlatesVotesSenderAfter[2] == approvals(slatesVotesSender[2]);
    require approvalsSlatesVotesSenderAfter[3] == approvals(slatesVotesSender[3]);
    require approvalsSlatesVotesSenderAfter[4] == approvals(slatesVotesSender[4]);
    uint256[] approvalsYaysAfter;
    require approvalsYaysAfter[0] == approvals(yays[0]);
    require approvalsYaysAfter[1] == approvals(yays[1]);
    require approvalsYaysAfter[2] == approvals(yays[2]);
    require approvalsYaysAfter[3] == approvals(yays[3]);
    require approvalsYaysAfter[4] == approvals(yays[4]);
    mathint approvalsSlatesOtherAfter = approvals(slatesOther);
    mathint depositsSender = deposits(e.msg.sender);

    uint256 vi;
    require vi < votesSenderLength;
    uint256 yi;
    require yi < yaysLength;

    assert slateYaysLength == yaysLength, "Assert 1";
    assert slatesSlateYays[yi] == yays[yi], "Assert 2";
    assert slatesOtherAnyAfter == slatesOtherAnyBefore, "Assert 3";
    assert votesSenderAfter == slateYays, "Assert 4";
    assert votesOtherAfter == votesOtherBefore, "Assert 5";
    assert (forall uint256 j. j < yaysLength => slatesVotesSender[vi] != yays[j]) => approvalsSlatesVotesSenderAfter[vi] == approvalsSlatesVotesSenderBefore[vi] - depositsSender, "Assert 6";
    assert (exists uint256 j. j < yaysLength && slatesVotesSender[vi] == yays[j]) => approvalsSlatesVotesSenderAfter[vi] == approvalsSlatesVotesSenderBefore[vi], "Assert 7";
    assert (forall uint256 j. j < votesSenderLength => yays[yi] != slatesVotesSender[j]) => approvalsYaysAfter[yi] == approvalsYaysBefore[yi] + depositsSender, "Assert 8";
    assert (exists uint256 j. j < votesSenderLength && yays[yi] == slatesVotesSender[j]) => approvalsYaysAfter[yi] == approvalsYaysBefore[yi], "Assert 9";
    assert approvalsSlatesOtherAfter == approvalsSlatesOtherBefore, "Assert 10";
}

// Verify revert rules on vote
rule vote_yays_revert(address[] yays) {
    env e;

    mathint yaysLength = yays.length;
    require yaysLength <= 20; // loop_iter limit but >>> maxYays

    mathint maxYays = maxYays();
    require maxYays == 5;

    bytes32 EMPTY_SLATE = EMPTY_SLATE();

    bytes32 slateYays = yaysLength <= maxYays ? aux.hashYays(yays) : to_bytes32(0); // To avoid an error on something that won't be used
    require to_mathint(length(slateYays)) <= maxYays; // Not possible to have an existing array larger than maxYays, but still needed for the prover

    bytes32 votesSender = votes(e.msg.sender);
    mathint votesSenderLength = length(votesSender);
    require votesSenderLength <= maxYays;
    address[] slatesVotesSender;
    require slatesVotesSender[0] == slates(votesSender, 0);
    require slatesVotesSender[1] == slates(votesSender, 1);
    require slatesVotesSender[2] == slates(votesSender, 2);
    require slatesVotesSender[3] == slates(votesSender, 3);
    require slatesVotesSender[4] == slates(votesSender, 4);
    // This is to avoid that the hash of the new voting array can collide with the hash of the prev existing voted (if not the same content)
    require votesSenderLength != yaysLength || (exists uint256 i. i < yaysLength && slatesVotesSender[i] != yays[i]) => votesSender != slateYays;
    require votesSenderLength <= 1 || (forall uint256 i. forall uint256 j. to_mathint(j) == i + 1 && j < votesSenderLength => slatesVotesSender[j] > slatesVotesSender[i]);
    uint256[] approvalsSlatesVotesSender;
    require approvalsSlatesVotesSender[0] == approvals(slatesVotesSender[0]);
    require approvalsSlatesVotesSender[1] == approvals(slatesVotesSender[1]);
    require approvalsSlatesVotesSender[2] == approvals(slatesVotesSender[2]);
    require approvalsSlatesVotesSender[3] == approvals(slatesVotesSender[3]);
    require approvalsSlatesVotesSender[4] == approvals(slatesVotesSender[4]);
    uint256[] approvalsYays;
    require approvalsYays[0] == approvals(yays[0]);
    require approvalsYays[1] == approvals(yays[1]);
    require approvalsYays[2] == approvals(yays[2]);
    require approvalsYays[3] == approvals(yays[3]);
    require approvalsYays[4] == approvals(yays[4]);
    mathint depositsSender = deposits(e.msg.sender);

    address yays0 = yays[0];
    address yays1 = yays[1];
    address yays2 = yays[2];
    address yays3 = yays[3];
    address yays4 = yays[4];

    address slatesVotesSender0 = slatesVotesSender[0];
    address slatesVotesSender1 = slatesVotesSender[1];
    address slatesVotesSender2 = slatesVotesSender[2];
    address slatesVotesSender3 = slatesVotesSender[3];
    address slatesVotesSender4 = slatesVotesSender[4];

    mathint approvalsYays0 = approvalsYays[0];
    mathint approvalsYays1 = approvalsYays[1];
    mathint approvalsYays2 = approvalsYays[2];
    mathint approvalsYays3 = approvalsYays[3];
    mathint approvalsYays4 = approvalsYays[4];

    vote@withrevert(e, yays);

    bool revert1  = e.msg.value > 0;
    bool revert2  = yaysLength > maxYays;
    bool revert3  = yaysLength > 1 && (exists uint256 i. exists uint256 j. to_mathint(j) == i + 1 && j < yaysLength && yays[j] <= yays[i]);
    bool revert4  = yaysLength == 0 && slateYays != EMPTY_SLATE;
    bool revert5  = exists uint256 i. i < votesSenderLength && approvalsSlatesVotesSender[i] < depositsSender;
    bool revert6  = yaysLength >= 1 &&
                    (forall uint256 i. i < votesSenderLength => yays[0] != slatesVotesSender[i]) && approvalsYays[0] + depositsSender > max_uint256;
    bool revert7  = yaysLength >= 2 &&
                    (forall uint256 i. i < votesSenderLength => yays[1] != slatesVotesSender[i]) && approvalsYays[1] + depositsSender > max_uint256;
    bool revert8  = yaysLength >= 3 &&
                    (forall uint256 i. i < votesSenderLength => yays[2] != slatesVotesSender[i]) && approvalsYays[2] + depositsSender > max_uint256;
    bool revert9  = yaysLength >= 4 &&
                    (forall uint256 i. i < votesSenderLength => yays[3] != slatesVotesSender[i]) && approvalsYays[3] + depositsSender > max_uint256;
    bool revert10 = yaysLength == 5 &&
                    (forall uint256 i. i < votesSenderLength => yays[4] != slatesVotesSender[i]) && approvalsYays[4] + depositsSender > max_uint256;

    bool reverts = revert1 || revert2 || revert3 || revert4 || revert5 || revert6 || revert7 || revert8 || revert9 || revert10;
    assert lastReverted => reverts, "Missing revert rules";
    assert reverts => lastReverted, "Revert rules failed";
}

// Verify correct storage changes for non reverting vote
rule vote_slate(bytes32 slate) {
    env e;

    mathint maxYays = maxYays();
    require maxYays == 5;

    address otherAddr;
    require otherAddr != e.msg.sender;

    bytes32 votesSenderBefore = votes(e.msg.sender);
    bytes32 votesOtherBefore = votes(otherAddr);
    mathint votesSenderLength = length(votesSenderBefore);
    require votesSenderLength <= maxYays;
    address[] slatesVotesSender;
    require slatesVotesSender[0] == slates(votesSenderBefore, 0);
    require slatesVotesSender[1] == slates(votesSenderBefore, 1);
    require slatesVotesSender[2] == slates(votesSenderBefore, 2);
    require slatesVotesSender[3] == slates(votesSenderBefore, 3);
    require slatesVotesSender[4] == slates(votesSenderBefore, 4);
    mathint slateLength = length(slate);
    require slateLength <= maxYays;
    address[] slatesSlate;
    require slatesSlate[0] == slates(slate, 0);
    require slatesSlate[1] == slates(slate, 1);
    require slatesSlate[2] == slates(slate, 2);
    require slatesSlate[3] == slates(slate, 3);
    require slatesSlate[4] == slates(slate, 4);
    // This is to avoid that the hash of the new voting array can collide with the hash of the prev existing voted (if not the same content)
    require votesSenderLength != slateLength || (exists uint256 i. i < slateLength && slatesVotesSender[i] != slatesSlate[i]) => votesSenderBefore != slate;
    require votesSenderLength <= 1 || (forall uint256 i. forall uint256 j. to_mathint(j) == i + 1 && j < votesSenderLength => slatesVotesSender[j] > slatesVotesSender[i]);
    require slateLength <= 1 || (forall uint256 i. forall uint256 j. to_mathint(j) == i + 1 && j < slateLength => slatesSlate[j] > slatesSlate[i]);
    address slatesOther;
    require forall uint256 i. i < votesSenderLength => slatesOther != slatesVotesSender[i];
    require forall uint256 i. i < slateLength => slatesOther != slatesSlate[i];
    uint256[] approvalsSlatesVotesSenderBefore;
    require approvalsSlatesVotesSenderBefore[0] == approvals(slatesVotesSender[0]);
    require approvalsSlatesVotesSenderBefore[1] == approvals(slatesVotesSender[1]);
    require approvalsSlatesVotesSenderBefore[2] == approvals(slatesVotesSender[2]);
    require approvalsSlatesVotesSenderBefore[3] == approvals(slatesVotesSender[3]);
    require approvalsSlatesVotesSenderBefore[4] == approvals(slatesVotesSender[4]);
    uint256[] approvalsSlatesSlateBefore;
    require approvalsSlatesSlateBefore[0] == approvals(slatesSlate[0]);
    require approvalsSlatesSlateBefore[1] == approvals(slatesSlate[1]);
    require approvalsSlatesSlateBefore[2] == approvals(slatesSlate[2]);
    require approvalsSlatesSlateBefore[3] == approvals(slatesSlate[3]);
    require approvalsSlatesSlateBefore[4] == approvals(slatesSlate[4]);
    mathint approvalsSlatesOtherBefore = approvals(slatesOther);
    mathint depositsSender = deposits(e.msg.sender);

    vote(e, slate);

    bytes32 votesSenderAfter = votes(e.msg.sender);
    bytes32 votesOtherAfter = votes(otherAddr);
    uint256[] approvalsSlatesVotesSenderAfter;
    require approvalsSlatesVotesSenderAfter[0] == approvals(slatesVotesSender[0]);
    require approvalsSlatesVotesSenderAfter[1] == approvals(slatesVotesSender[1]);
    require approvalsSlatesVotesSenderAfter[2] == approvals(slatesVotesSender[2]);
    require approvalsSlatesVotesSenderAfter[3] == approvals(slatesVotesSender[3]);
    require approvalsSlatesVotesSenderAfter[4] == approvals(slatesVotesSender[4]);
    uint256[] approvalsSlatesSlateAfter;
    require approvalsSlatesSlateAfter[0] == approvals(slatesSlate[0]);
    require approvalsSlatesSlateAfter[1] == approvals(slatesSlate[1]);
    require approvalsSlatesSlateAfter[2] == approvals(slatesSlate[2]);
    require approvalsSlatesSlateAfter[3] == approvals(slatesSlate[3]);
    require approvalsSlatesSlateAfter[4] == approvals(slatesSlate[4]);
    mathint approvalsSlatesOtherAfter = approvals(slatesOther);

    uint256 vi;
    require vi < votesSenderLength;
    uint256 si;
    require si < slateLength;

    assert votesSenderAfter == slate, "Assert 1";
    assert votesOtherAfter == votesOtherBefore, "Assert 2";
    assert (forall uint256 j. j < slateLength => slatesVotesSender[vi] != slatesSlate[j]) => approvalsSlatesVotesSenderAfter[vi] == approvalsSlatesVotesSenderBefore[vi] - depositsSender, "Assert 3";
    assert (exists uint256 j. j < slateLength && slatesVotesSender[vi] == slatesSlate[j]) => approvalsSlatesVotesSenderAfter[vi] == approvalsSlatesVotesSenderBefore[vi], "Assert 4";
    assert (forall uint256 j. j < votesSenderLength => slatesSlate[si] != slatesVotesSender[j]) => approvalsSlatesSlateAfter[si] == approvalsSlatesSlateBefore[si] + depositsSender, "Assert 5";
    assert (exists uint256 j. j < votesSenderLength && slatesSlate[si] == slatesVotesSender[j]) => approvalsSlatesSlateAfter[si] == approvalsSlatesSlateBefore[si], "Assert 6";
    assert approvalsSlatesOtherAfter == approvalsSlatesOtherBefore, "Assert 7";
}

// Verify revert rules on vote
rule vote_slate_revert(bytes32 slate) {
    env e;

    mathint maxYays = maxYays();
    require maxYays == 5;

    bytes32 EMPTY_SLATE = EMPTY_SLATE();

    bytes32 votesSender = votes(e.msg.sender);
    mathint votesSenderLength = length(votesSender);
    require votesSenderLength <= maxYays;
    address[] slatesVotesSender;
    require slatesVotesSender[0] == slates(votesSender, 0);
    require slatesVotesSender[1] == slates(votesSender, 1);
    require slatesVotesSender[2] == slates(votesSender, 2);
    require slatesVotesSender[3] == slates(votesSender, 3);
    require slatesVotesSender[4] == slates(votesSender, 4);
    mathint slateLength = length(slate);
    require slateLength <= maxYays; // Not possible to have an existing array larger than maxYays, but still needed for the prover
    address[] slatesSlate;
    require slatesSlate[0] == slates(slate, 0);
    require slatesSlate[1] == slates(slate, 1);
    require slatesSlate[2] == slates(slate, 2);
    require slatesSlate[3] == slates(slate, 3);
    require slatesSlate[4] == slates(slate, 4);
    // This is to avoid that the hash of the new voting array can collide with the hash of the prev existing voted (if not the same content)
    require votesSenderLength != slateLength || (exists uint256 i. i < slateLength && slatesVotesSender[i] != slatesSlate[i]) => votesSender != slate;
    require votesSenderLength <= 1 || (forall uint256 i. forall uint256 j. to_mathint(j) == i + 1 && j < votesSenderLength => slatesVotesSender[j] > slatesVotesSender[i]);
    require slateLength <= 1 || (forall uint256 i. forall uint256 j. to_mathint(j) == i + 1 && j < slateLength => slatesSlate[j] > slatesSlate[i]);
    uint256[] approvalsSlatesVotesSender;
    require approvalsSlatesVotesSender[0] == approvals(slatesVotesSender[0]);
    require approvalsSlatesVotesSender[1] == approvals(slatesVotesSender[1]);
    require approvalsSlatesVotesSender[2] == approvals(slatesVotesSender[2]);
    require approvalsSlatesVotesSender[3] == approvals(slatesVotesSender[3]);
    require approvalsSlatesVotesSender[4] == approvals(slatesVotesSender[4]);
    uint256[] approvalsSlatesSlate;
    require approvalsSlatesSlate[0] == approvals(slatesSlate[0]);
    require approvalsSlatesSlate[1] == approvals(slatesSlate[1]);
    require approvalsSlatesSlate[2] == approvals(slatesSlate[2]);
    require approvalsSlatesSlate[3] == approvals(slatesSlate[3]);
    require approvalsSlatesSlate[4] == approvals(slatesSlate[4]);
    mathint depositsSender = deposits(e.msg.sender);

    vote@withrevert(e, slate);

    bool revert1  = e.msg.value > 0;
    bool revert2  = slateLength == 0 && slate != EMPTY_SLATE;
    bool revert3  = exists uint256 i. i < votesSenderLength && approvalsSlatesVotesSender[i] < depositsSender;
    bool revert4  = slateLength >= 1 &&
                    (forall uint256 i. i < votesSenderLength => slatesSlate[0] != slatesVotesSender[i]) && approvalsSlatesSlate[0] + depositsSender > max_uint256;
    bool revert5  = slateLength >= 2 &&
                    (forall uint256 i. i < votesSenderLength => slatesSlate[1] != slatesVotesSender[i]) && approvalsSlatesSlate[1] + depositsSender > max_uint256;
    bool revert6  = slateLength >= 3 &&
                    (forall uint256 i. i < votesSenderLength => slatesSlate[2] != slatesVotesSender[i]) && approvalsSlatesSlate[2] + depositsSender > max_uint256;
    bool revert7  = slateLength >= 4 &&
                    (forall uint256 i. i < votesSenderLength => slatesSlate[3] != slatesVotesSender[i]) && approvalsSlatesSlate[3] + depositsSender > max_uint256;
    bool revert8 = slateLength == 5 &&
                    (forall uint256 i. i < votesSenderLength => slatesSlate[4] != slatesVotesSender[i]) && approvalsSlatesSlate[4] + depositsSender > max_uint256;

    bool reverts = revert1 || revert2 || revert3 || revert4 || revert5 || revert6 || revert7 || revert8;
    assert lastReverted => reverts, "Missing revert rules";
    assert reverts => lastReverted, "Revert rules failed";
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
