"""
This file collects different functions for estimating the semivariance of a group of values. These functions
can be used to fit a experimental variogram to a list of points. Each of the given functions just calculate
the estimate for one bin. If you want a Variogram, use the variogram functions or Class from the Variogram and vario
submodule, or order the bins yourself
"""
import numpy as np
from scipy.special import binom
from numba import jit


@jit
def matheron(x):
    r"""Matheron Semi-Variance

    Calculates the Matheron Semi-Variance from an array of pairwise differences.
    Returns the semi-variance for the whole array. In case a semi-variance is
    needed for multiple groups, this function has to be mapped on each group.
    That is the typical use case in geostatistics.

    Parameters
    ----------
    x : numpy.ndarray
        Array of pairwise differences. These values should be the distances
        between pairwise observations in value space. If xi and x[i+h] fall
        into the h separating distance class, x should contain abs(xi - x[i+h])
        as an element.

    Returns
    -------
    numpy.float64

    Notes
    -----

    This implementation is done after the original publication [1]_ and the
    notes on their application [2]_. Following [1]_, the semi-variance is
    calculated as:

    .. math ::
        \gamma (h) = \frac{1}{2N(h)} * \sum_{i=1}^{N(h)}(x)^2

    with:

    .. math ::
        x = (Z(x_i) - Z(x_{i+1})

     where x is exactly the input array x.

    References
    ----------

    .. [1] Matheron, G. (1962): Traité de Géostatistique Appliqué, Tonne 1.
       Memoires de Bureau de Recherches Géologiques et Miniéres, Paris.

    .. [2] Matheron, G. (1965): Les variables regionalisées et leur estimation.
       Editions Masson et Cie, 212 S., Paris.

    """
    # convert
    x = np.asarray(x)

    # prevent ZeroDivisionError
    if x.size == 0:
        return np.nan

    return (1. / (2 * x.size)) * np.sum(np.power(x, 2))


@jit
def cressie(x):
    r""" Cressie-Hawkins Semi-Variance

    Calculates the Cressie-Hawkins Semi-Variance from an array of pairwise
    differences. Returns the semi-variance for the whole array. In case a
    semi-variance is needed for multiple groups, this function has to be
    mapped on each group. That is the typical use case in geostatistics.

    Parameters
    ----------
    x : numpy.ndarray
        Array of pairwise differences. These values should be the distances
        between pairwise observations in value space. If xi and x[i+h] fall
        into the h separating distance class, x should contain abs(xi - x[i+h])
        as an element.

    Returns
    -------
    numpy.float64

    Notes
    -----

    This implementation is done after the publication by Cressie and Hawkins
    from 1980 [3]_:

    .. math ::
        2\gamma (h) = \frac{(\frac{1}{N(h)} \sum_{i=1}^{N(h)} |x|^{0.5})^4}
        {0.457 + \frac{0.494}{N(h)} + \frac{0.045}{N^2(h)}}

    with:

    .. math ::
        x = (Z(x_i) - Z(x_{i+1})

     where x is exactly the input array x.

    References
    ----------

    .. [3] Cressie, N., and D. Hawkins (1980): Robust estimation of the
       variogram. Math. Geol., 12, 115-125.


    """
    # convert
    x = np.asarray(x)

    # get the length
    n = x.size

    # prevent ZeroDivisionError
    if n == 0:
        return np.nan

    # Nominator
    nominator = np.power((1 / n) * np.sum(np.power(x, 0.5)), 4)

    # Denominator
    denominator = 0.457 + (0.494 / n) + (0.045 / n**2)

    return nominator / (2 * denominator)


def dowd(x):
    r"""Dowd semi-variance

    Calculates the Dowd semi-variance from an array of pairwise
    differences. Returns the semi-variance for the whole array. In case a
    semi-variance is needed for multiple groups, this function has to be
    mapped on each group. That is the typical use case in geostatistics.

    Parameters
    ----------
    x : numpy.ndarray
        Array of pairwise differences. These values should be the distances
        between pairwise observations in value space. If xi and x[i+h] fall
        into the h separating distance class, x should contain abs(xi - x[i+h])
        as an element.

    Returns
    -------
    numpy.float64

    Notes
    -----
    The Dowd estimator is based on the median of all pairwise differences in
    each lag class and is therefore robust to exteme values at the cost of
    variability.
    This implementation is done after the publication _[4]:

    .. math::

        2\gamma (h) = 2.198 * {median(x)}^2

    with:

    .. math::
        x = (Z(x_i) - Z(x_{i+1})

    where x is exactly the input array x.

    References
    ----------

    .. [4] Dowd, P. A., (1984): The variogram and kriging: Robust and resistant
       estimators, in Geostatistics for Natural Resources Characterization.
       Edited by G. Verly et al., pp. 91 - 106, D. Reidel, Dordrecht.

    """
    # convert
    x = np.asarray(x)

    return 2.198 * np.nanmedian(x)**2


@jit
def genton(x):
    r""" Genton robust semi-variance estimator

    Return the Genton semi-variance of the given sample x. Genton is a highly
    robust varigram estimator, that is designed to be location free and
    robust on extreme values in x.
    Genton is based on calculating kth order statistics and will for large
    data sets be close or equal to the 25% quartile of all ordered point pairs
    in X.

    Parameters
    ----------
    x : numpy.ndarray
        Array of pairwise differences. These values should be the distances
        between pairwise observations in value space. If xi and x[i+h] fall
        into the h separating distance class, x should contain abs(xi - x[i+h])
        as an element.

    Returns
    -------
    numpy.float64

    Notes
    -----
    The Genton estimator is described in great detail in the original
    publication [1]_ and befined as:

    .. math:: Q_{N_h} = 2.2191\{|V_i(h) - V_j(h)|; i < j\}_{(k)}

    and

     .. math:: k = \binom{[N_h / 2] + 1}{2}

     and

     .. math:: q = \binom{N_h}{2}

     where k is the kth quantile of all q point pairs. For large N (k/q) will be
     close to 0.25. For N >= 500, (k/q) is close to 0.25 by two decimals and
     will therefore be set to 0.5 and the two binomial coefficients k,
     q are not calculated.

    References
    ----------

    ..  [1] Genton, M. G., (1998): Highly robust variogram estimation,
        Math. Geol., 30, 213 - 221.

    """
    x = np.array(x)

    # get length
    n = x.size

    if n < 2:
        return np.nan

    # pre-populate y => we need (n*n -n) / 2
    y = np.zeros(int((n*n - n) / 2))

    # calculate
    z = 0
    for i in range(n):
        for j in range(n):
            if i < j:
                y[z] = np.abs(x[i] - x[j])
                z += 1

    # if N > 500, (k/q) will be ~ 1/4 anyway
    if n >= 500:
        k, q, = 1, 4
    else:
        # get k  k is binom(N(x)/2+1, 2)
        k = binom(n / 2 + 1, 2)

        # get q. Genton needs the kth quantile of q
        q = binom(n, 2)

    # return the kth percentile
    return 0.5 * np.power(2.219 * np.percentile(y, (k / q)), 2)


def minmax(x):
    """Minimum - Maximum Estimator

    Returns a custom value. This estimator is the difference of maximum and
    minimum pairwise differences, normalized by the mean. MinMax will be very
    sensitive to extreme values.

    Do only use this estimator, in case you know what you are doing. It is
    experimental and might change its behaviour in a future version.

    Parameters
    ----------
    x : numpy.ndarray
        Array of pairwise differences. These values should be the distances
        between pairwise observations in value space. If xi and x[i+h] fall
        into the h separating distance class, x should contain abs(xi - x[i+h])
        as an element.

    Returns
    -------
    numpy.float64

    """
    x = np.asarray(x)

    return (np.nanmax(x) - np.nanmin(x)) / np.nanmean(x)


def percentile(x, p=50):
    """Percentile estimator

    Returns a given percentile as semi-variance. Do only use this estimator,
    in case you know what you are doing.

    Do only use this estimator, in case you know what you are doing. It is
    experimental and might change its behaviour in a future version.

    Parameters
    ----------
    x : numpy.ndarray
        Array of pairwise differences. These values should be the distances
        between pairwise observations in value space. If xi and x[i+h] fall
        into the h separating distance class, x should contain abs(xi - x[i+h])
        as an element.
    p : int
        Desired percentile. Should be given as whole numbers 0 < p < 100.

    Returns
    -------
    np.float64

    """
    x = np.asarray(x)

    return np.percentile(x, q=p)


def entropy_depr(X, bins=None):
    """
    Use the Shannon Entropy H to describe the distribution of the given sample.
    For calculating the Shannon Entropy, the bin edges are needed and can be passed as pk.
    If pk is None, these edges will be calculated using the numpy.histogram function with bins='fq'.
    This uses Freedman Diacons Estimator and is fairly resilient to outliers.
    If the input data X is 2D (Entropy for more than one bin needed), it will derive the histogram once and
    use the same edges in all bins.
    CAUTION: this is actually an changed behaviour to scikit-gstat<=0.1.5

    # TODO: handle the 0s in output of X

    :param X:  np.ndarray with the given sample to calculate the Shannon entropy from
    :param bins: The bin edges for entropy calculation, or an amount of even spaced bins
    :return:
    """
    _X = np.array(X)

    # helper function
    ppairs = lambda x: [np.abs(x[i] - x[i+1]) for i in np.arange(0, len(x), 2)]

    if any([isinstance(_, (list, np.ndarray)) for _ in _X]):
        # if bins is not set, use the histogram over the full value range
        if bins is None:
            # could not fiugre out a better way here. I need the values before calculating the entropy
            # in order to use the full value range in all bins
            allp = [ppairs(_) for _ in _X]
            minv = np.min(list(map(np.min, allp)))
            maxv = np.max(list(map(np.max, allp)))
            bins = np.linspace(minv, maxv, 50).tolist() + [maxv] # have no better idea to include the end edge as well
        return np.array([entropy(_, bins=bins) for _ in _X])

    # check even
    if len(_X) % 2 > 0:
        raise ValueError('The sample does not have an even length: {}'.format(_X))

    # calculate the values
    vals = ppairs(_X)

    # claculate the bins
    if bins is None:
        bins = 15

    # get the amounts
    amt = np.histogram(vals, bins=bins)[0]

    # add a very small value to the p, otherwise the log2 will be -inf.
    p = (amt / np.sum(amt)) + 1e-5
    info = lambda p: -np.log2(p)

    # map info to p and return the inner product
    return np.fromiter(map(info, p), dtype=np.float).dot(p)

